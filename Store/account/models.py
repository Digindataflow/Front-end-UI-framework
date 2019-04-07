from django.db import models

# Create your models here.
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)

class UserManager(BaseUserManager):
    """Manager for user without username

    """
    use_in_migrations = True

    def _create_user(self, email, password,**extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(
            "Superuser must have is_staff=True."
            )
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
            "Superuser must have is_superuser=True."
            )
        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    """User model withour username.

    Email is used as username.

    """
    username = None
    email = models.EmailField('email address', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    @property
    def is_employee(self):
        return self.is_active and (
            self.is_superuser
            or self.is_staff
            and self.groups.filter(name="Employees").exists()
        )

    @property
    def is_dispatcher(self):
        return self.is_active and (
            self.is_superuser
            or self.is_staff
            and self.groups.filter(name="Dispatchers").exists()
        )

class Address(models.Model):
    SUPPORTED_COUNTRIES = (
        ("uk", "United Kingdom"),
        ("us", "United States of America"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    address1 = models.CharField("Address line 1", max_length=60)
    address2 = models.CharField(
        "Address line 2", max_length=60, blank=True
    )
    zip_code = models.CharField(
        "ZIP / Postal code", max_length=12
    )
    city = models.CharField(max_length=60)
    country = models.CharField(
        max_length=3, choices=SUPPORTED_COUNTRIES
    )
    def __str__(self):
        return ", ".join([
            self.name,
            self.address1,
            self.address2,
            self.zip_code,
            self.city,
            self.country,
        ])