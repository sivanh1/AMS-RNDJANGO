
from datetime import timedelta
from .models import SystemSettings, Attendance, LeaveRequest, WFHRequest


def get_system_date():
    return SystemSettings.get_system_date()


def has_approved_leave(user, target_date):

    return LeaveRequest.objects.filter(
        user=user,
        status='approved',
        start_date__lte=target_date,
        end_date__gte=target_date,
    ).exists()


def has_approved_wfh(user, target_date):

    return WFHRequest.objects.filter(
        user=user,
        status='approved',
        date=target_date,
    ).exists()


def check_leave_overlap(user, start_date, end_date, exclude_pk=None):
 
    # Overlap with other leave requests (not rejected)
    leaves = LeaveRequest.objects.filter(
        user=user,
        start_date__lte=end_date,
        end_date__gte=start_date,
    ).exclude(status='rejected')
    if exclude_pk:
        leaves = leaves.exclude(pk=exclude_pk)
    if leaves.exists():
        return True

    # Overlap with approved WFH
    wfh_exists = WFHRequest.objects.filter(
        user=user,
        date__gte=start_date,
        date__lte=end_date,
    ).exclude(status='rejected').exists()
    return wfh_exists


def check_wfh_overlap(user, wfh_date, exclude_pk=None):

    # Overlap with other WFH requests
    wfhs = WFHRequest.objects.filter(
        user=user,
        date=wfh_date,
    ).exclude(status='rejected')
    if exclude_pk:
        wfhs = wfhs.exclude(pk=exclude_pk)
    if wfhs.exists():
        return True

    # Overlap with leave requests
    leave_exists = LeaveRequest.objects.filter(
        user=user,
        start_date__lte=wfh_date,
        end_date__gte=wfh_date,
    ).exclude(status='rejected').exists()
    return leave_exists


def create_attendance_for_leave(leave):

    current = leave.start_date
    records = []
    while current <= leave.end_date:
        if not Attendance.objects.filter(user=leave.user, date=current).exists():
            records.append(Attendance(
                user=leave.user,
                date=current,
                status='leave',
            ))
        current += timedelta(days=1)
    if records:
        Attendance.objects.bulk_create(records, ignore_conflicts=True)


def create_attendance_for_wfh(wfh):
    
    Attendance.objects.update_or_create(
        user=wfh.user,
        date=wfh.date,
        defaults={'status': 'wfh'},
    )
