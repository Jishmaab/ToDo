from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class UserChoices(models.IntegerChoices):
        Admin = 0, 'Admin'
        User = 1, 'User'
    user_type = models.IntegerField(choices=UserChoices.choices, default=1)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'User'


class TaskCategory(models.Model):
    name = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        db_table = 'TaskCategory'


class Task(models.Model):
    class StatusChoices(models.IntegerChoices):
        completed = 0, 'completed '
        incomplete = 1, 'incomplete'

    class PriorityChoices(models.IntegerChoices):
        low = 0, 'low',
        medium = 1, 'medium',
        high = 2, 'high'
        
    name = models.CharField(max_length=30, null=True, blank=True)
    category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE)
    due_date = models.DateField(null=True, blank=True)
    status = models.IntegerField(choices=StatusChoices.choices, default=0)
    priority = models.IntegerField(choices=PriorityChoices.choices, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    

    @property
    def is_expired(self) -> bool:
        return self.due_date > date.today()

    class Meta:
        db_table = 'Task'
