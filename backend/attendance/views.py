from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from datetime import date, datetime
from .models import Attendance, LeaveRequest
from .serializers import AttendanceSerializer, LeaveRequestSerializer, UserSerializer


# ── Auth ──────────────────────────────────────────────────────

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


# ── User ──────────────────────────────────────────────────────

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        attendance_today = Attendance.objects.filter(
            user=request.user, date=today
        ).first()
        leave_requests = LeaveRequest.objects.filter(
            user=request.user
        ).order_by('-created_at')
        attendance_records = Attendance.objects.filter(
            user=request.user
        ).order_by('date')

        return Response({
            'today': str(today),
            'attendance_today': AttendanceSerializer(attendance_today).data if attendance_today else None,
            'leave_requests': LeaveRequestSerializer(leave_requests, many=True).data,
            'attendance_records': AttendanceSerializer(attendance_records, many=True).data,
        })


class MarkAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_staff:
            return Response({'error': 'Admins cannot mark attendance.'}, status=403)

        today = date.today()

        if Attendance.objects.filter(user=request.user, date=today).exists():
            return Response({'error': 'Attendance already marked for today.'}, status=400)

        status_val = request.data.get('status')
        if status_val not in ['present', 'wfh']:
            return Response({'error': 'Invalid status.'}, status=400)

        att = Attendance.objects.create(
            user=request.user,
            date=today,
            status=status_val,
            marked_at=datetime.now()
        )
        return Response({
            'message': f'Marked as {"Present" if status_val == "present" else "WFH"}.',
            'attendance': AttendanceSerializer(att).data,
        })


class SubmitLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_staff:
            return Response({'error': 'Admins cannot submit leave.'}, status=403)

        try:
            start = date.fromisoformat(request.data.get('start_date', ''))
            end = date.fromisoformat(request.data.get('end_date', ''))
        except ValueError:
            return Response({'error': 'Invalid dates.'}, status=400)

        if end < start:
            return Response({'error': 'End date cannot be before start date.'}, status=400)
        if start < date.today():
            return Response({'error': 'Start date cannot be in the past.'}, status=400)

        reason = request.data.get('reason', '')
        if not reason:
            return Response({'error': 'Reason is required.'}, status=400)

        leave = LeaveRequest.objects.create(
            user=request.user,
            start_date=start,
            end_date=end,
            reason=reason,
        )
        return Response({
            'message': f'Leave submitted for {leave.num_days} day(s).',
            'leave': LeaveRequestSerializer(leave).data,
        }, status=201)


# ── Admin ──────────────────────────────────────────────────────

class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden.'}, status=403)

        today = date.today()
        today_att = Attendance.objects.filter(date=today).select_related('user')
        pending = LeaveRequest.objects.filter(status='pending').select_related('user')
        done = LeaveRequest.objects.exclude(status='pending').select_related('user')

        return Response({
            'today': str(today),
            'today_attendance': AttendanceSerializer(today_att, many=True).data,
            'today_present': today_att.filter(status='present').count(),
            'today_wfh': today_att.filter(status='wfh').count(),
            'today_total': today_att.count(),
            'pending_leaves': LeaveRequestSerializer(pending, many=True).data,
            'done_leaves': LeaveRequestSerializer(done, many=True).data,
        })


class ActionLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, action):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden.'}, status=403)
        if action not in ['approved', 'rejected']:
            return Response({'error': 'Invalid action.'}, status=400)

        try:
            leave = LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)

        leave.status = action
        leave.save()
        return Response({'message': f'Leave {action}.', 'leave': LeaveRequestSerializer(leave).data})
