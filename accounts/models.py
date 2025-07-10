from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ("APPLICANT", "متقاضی"),
        ("STAFF", "پرسنل"),
        ("ADMIN", "مدیر"),
    )
    

    GENDER_CHOICES = (
        ('male', 'آقا'),
        ('female', 'خانم'),
    )
    
    phone_number = models.CharField(max_length=15, unique=True, verbose_name="شماره تلفن")
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default="APPLICANT", verbose_name="نوع کاربر")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="جنسیت", blank=True, null=True)

    def __str__(self):
        return self.username