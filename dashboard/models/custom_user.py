from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):

    # 🔹 Keep username (already unique in AbstractUser)
    username = models.CharField(max_length=150, unique=True)

    # 🔹 Names
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    # 🔹 Email (also unique)
    email = models.EmailField(unique=True)

    # 🔹 Profile Picture
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        default='profile_pictures/default_avatar.jpg',
        blank=True,
        null=True
    )

    # 🔹 Role
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('operator', 'Operator'),
        ('user', 'User'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    # 🔹 Status
    is_active = models.BooleanField(default=True)

    # 🔹 Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 🔥 IMPORTANT
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return self.username