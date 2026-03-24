from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('wfh', 'Work From Home'),
        ('leave', 'On Leave'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_at = models.DateTimeField(default=datetime.now)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.status}"


class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=datetime.now)

    @property
    def num_days(self):
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"{self.user.username} - {self.start_date} ({self.status})"
