from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Attendance, LeaveRequest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_staff']


class AttendanceSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    marked_at_str = serializers.SerializerMethodField()

    def get_marked_at_str(self, obj):
        return obj.marked_at.strftime('%I:%M %p') if obj.marked_at else None

    class Meta:
        model = Attendance
        fields = ['id', 'username', 'date', 'status', 'marked_at_str']


class LeaveRequestSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    num_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = LeaveRequest
        fields = ['id', 'username', 'start_date', 'end_date', 'reason', 'status', 'num_days', 'created_at']
