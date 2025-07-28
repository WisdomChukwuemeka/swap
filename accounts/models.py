from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import random

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role='create', **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        if role == 'create':
            extra_fields.setdefault('is_staff', True)
            extra_fields.setdefault('is_superuser', False)
        elif role == 'offer':
            extra_fields.setdefault('is_staff', False)
            extra_fields.setdefault('is_superuser', False)
            
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_manager', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError("is_superuser must be set to is_staff=True")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("is_superuser must be set to is_superuser=True")
        if extra_fields.get('is_manager') is not True:
            raise ValueError("is_superuser must be set to is_manager=True")
        return self.create_user(email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('create', 'Create'),
        ('offer', 'Offer'),
    ]
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    agreement = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='create', null=False, blank=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        return self.email
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='images/avatar', blank=True, null=True)
    full_name = models.CharField(max_length=30, blank=False, null=False)
    phone_number = models.CharField(max_length=20)
    bio = models.TextField(max_length=300, blank=True, null=True)
    address = models.TextField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.avatar
    
