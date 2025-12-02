from django.contrib.auth.models import AbstractUser
from django.db import models
import os

class CustomUser(AbstractUser):
    LECTURER = 1
    AUDITOR = 2

    ROLE_CHOICES = [
        (LECTURER, 'Lecturer'),
        (AUDITOR, 'Auditor'),
    ]

    role = models.IntegerField(choices=ROLE_CHOICES, default=LECTURER)
    # Add related_name arguments to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='user',
    )
    


class MarkingTask(models.Model):
    assign_title = models.CharField(max_length=100)
    files = models.FileField(upload_to='marking_tasks/')  # Folder containing all files to be marked
    marking_scheme = models.FileField(upload_to='marking_schemes/')  # Marking scheme file
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='uploaded_marking_tasks', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.assign_title
    
class Report(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
    ]
    marking_task = models.ForeignKey(MarkingTask, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Assuming lecturer can be a CustomUser
    report_text = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
