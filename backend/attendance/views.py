from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone

from .models import Attendance, LeaveRequest, WFHRequest, SystemSettings
from .serializers import (
    AttendanceSerializer, LeaveRequestSerializer,
    WFHRequestSerializer, UserSerializer, SystemSettingsSerializer,
)
from .services import (
    get_system_date, has_approved_leave, has_approved_wfh,
    check_leave_overlap, create_attendance_for_leave,
    create_attendance_for_wfh,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        password2 = request.data.get('password2', '')

        if not username or not password:
            return Response({'error': 'Username and password required.'}, status=400)
        if password != password2:
            return Response({'error': 'Passwords do not match.'}, status=400)
        if len(password) < 6:
            return Response({'error': 'Password must be at least 6 characters.'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already taken.'}, status=400)

        user = User.objects.create_user(username=username, password=password)
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({'error': 'Invalid username or password.'}, status=401)
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = get_system_date()
        attendance_today = Attendance.objects.filter(
            user=request.user, date=today
        ).select_related('user').first()

        leave_requests = LeaveRequest.objects.filter(
            user=request.user
        ).select_related('user', 'actioned_by').order_by('-created_at')

        wfh_requests = WFHRequest.objects.filter(
            user=request.user
        ).select_related('user', 'actioned_by').order_by('-created_at')

        attendance_records = Attendance.objects.filter(
            user=request.user
        ).select_related('user').order_by('-date')

        has_leave = has_approved_leave(request.user, today)
        has_wfh = has_approved_wfh(request.user, today)

        return Response({
            'today': str(today),
            'attendance_today': AttendanceSerializer(attendance_today).data if attendance_today else None,
            'leave_requests': LeaveRequestSerializer(leave_requests, many=True).data,
            'wfh_requests': WFHRequestSerializer(wfh_requests, many=True).data,
            'attendance_records': AttendanceSerializer(attendance_records, many=True).data,
            'has_approved_leave_today': has_leave,
            'has_approved_wfh_today': has_wfh,
        })


class MarkAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_staff:
            return Response({'error': 'Admins cannot mark attendance.'}, status=403)

        today = get_system_date()

        # Already marked
        if Attendance.objects.filter(user=request.user, date=today).exists():
            return Response({'error': 'Attendance already marked for today.'}, status=400)

        # Approved leave exists → block
        if has_approved_leave(request.user, today):
            return Response({'error': 'You have an approved leave for today.'}, status=400)

        # Approved WFH exists → force wfh
        if has_approved_wfh(request.user, today):
            status_val = 'wfh'
        else:
            status_val = request.data.get('status')
            if status_val not in ['present', 'wfh']:
                return Response({'error': 'Invalid status.'}, status=400)

        att = Attendance.objects.create(
            user=request.user,
            date=today,
            status=status_val,
        )
        label = {'present': 'Present', 'wfh': 'WFH'}.get(status_val, status_val.upper())
        return Response({
            'message': f'Marked as {label}.',
            'attendance': AttendanceSerializer(att).data,
        })


class SubmitLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_staff:
            return Response({'error': 'Admins cannot submit leave.'}, status=403)

        serializer = LeaveRequestSerializer(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            # Return first error as flat string
            errors = serializer.errors
            if 'non_field_errors' in errors:
                msg = errors['non_field_errors'][0]
            else:
                msg = next(iter(
                    v[0] if isinstance(v, list) else v
                    for v in errors.values()
                ), 'Validation error.')
            return Response({'error': str(msg)}, status=400)

        leave = LeaveRequest.objects.create(
            user=request.user,
            start_date=serializer.validated_data['start_date'],
            end_date=serializer.validated_data['end_date'],
            reason=serializer.validated_data['reason'],
        )
        return Response({
            'message': f'Leave submitted for {leave.num_days} day(s).',
            'leave': LeaveRequestSerializer(leave).data,
        }, status=201)


class ApplyWFHView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_staff:
            return Response({'error': 'Admins cannot apply for WFH.'}, status=403)

        # Accept either 'date' or 'start_date' from frontend
        data = request.data.copy()
        if 'date' not in data and 'start_date' in data:
            data['date'] = data['start_date']

        serializer = WFHRequestSerializer(
            data=data,
            context={'request': request},
        )
        if not serializer.is_valid():
            errors = serializer.errors
            if 'non_field_errors' in errors:
                msg = errors['non_field_errors'][0]
            else:
                msg = next(iter(
                    v[0] if isinstance(v, list) else v
                    for v in errors.values()
                ), 'Validation error.')
            return Response({'error': str(msg)}, status=400)

        wfh = WFHRequest.objects.create(
            user=request.user,
            date=serializer.validated_data['date'],
            reason=serializer.validated_data['reason'],
        )
        return Response({
            'message': 'WFH request submitted.',
            'wfh': WFHRequestSerializer(wfh).data,
        }, status=201)


class MyWFHView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = WFHRequest.objects.filter(
            user=request.user
        ).select_related('user', 'actioned_by')
        return Response(WFHRequestSerializer(qs, many=True).data)



class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden.'}, status=403)

        today = get_system_date()
        today_att = Attendance.objects.filter(date=today).select_related('user')
        pending_leaves = LeaveRequest.objects.filter(
            status='pending'
        ).select_related('user')
        done_leaves = LeaveRequest.objects.exclude(
            status='pending'
        ).select_related('user', 'actioned_by')
        pending_wfh = WFHRequest.objects.filter(
            status='pending'
        ).select_related('user')

        return Response({
            'today': str(today),
            'today_attendance': AttendanceSerializer(today_att, many=True).data,
            'today_present': today_att.filter(status='present').count(),
            'today_wfh': today_att.filter(status='wfh').count(),
            'today_leave': today_att.filter(status='leave').count(),
            'today_total': today_att.count(),
            'pending_leaves': LeaveRequestSerializer(pending_leaves, many=True).data,
            'done_leaves': LeaveRequestSerializer(done_leaves, many=True).data,
            'pending_wfh': WFHRequestSerializer(pending_wfh, many=True).data,
            'pending_wfh_count': pending_wfh.count(),
        })


class ActionLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, action):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden.'}, status=403)
        if action not in ['approved', 'rejected']:
            return Response({'error': 'Invalid action.'}, status=400)

        try:
            leave = LeaveRequest.objects.select_related('user').get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)

        leave.status = action
        leave.actioned_by = request.user
        leave.actioned_at = timezone.now()
        leave.save()

        # Auto-create attendance records on approval
        if action == 'approved':
            create_attendance_for_leave(leave)

        return Response({
            'message': f'Leave {action}.',
            'leave': LeaveRequestSerializer(leave).data,
        })


class AdminPendingWFHView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden.'}, status=403)
        qs = WFHRequest.objects.filter(
            status='pending'
        ).select_related('user')
        return Response(WFHRequestSerializer(qs, many=True).data)


class ActionWFHView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, action):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden.'}, status=403)
        if action not in ['approved', 'rejected']:
            return Response({'error': 'Invalid action.'}, status=400)

        try:
            wfh = WFHRequest.objects.select_related('user').get(pk=pk)
        except WFHRequest.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)

        wfh.status = action
        wfh.actioned_by = request.user
        wfh.actioned_at = timezone.now()
        wfh.save()

        if action == 'approved':
            create_attendance_for_wfh(wfh)

        return Response({
            'message': f'WFH request {action}.',
            'wfh': WFHRequestSerializer(wfh).data,
        })


class SystemDateView(APIView):
    """Admin-only: GET current system date, POST to update it."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden.'}, status=403)
        today = get_system_date()
        return Response({'current_date': str(today)})

    def post(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden.'}, status=403)

        serializer = SystemSettingsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        obj, _ = SystemSettings.objects.get_or_create(pk=1)
        obj.current_date = serializer.validated_data['current_date']
        obj.save()
        return Response({
            'message': 'System date updated.',
            'current_date': str(obj.current_date),
        })


class AdminAllAttendanceView(APIView):
    """Admin-only: GET all attendance records (optionally filter by date)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden.'}, status=403)

        qs = Attendance.objects.all().select_related('user').order_by('-date')
        date_filter = request.query_params.get('date')
        if date_filter:
            qs = qs.filter(date=date_filter)
        return Response(AttendanceSerializer(qs[:200], many=True).data)
