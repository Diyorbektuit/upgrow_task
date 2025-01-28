from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import UserManager as AbstractUserManager, AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken

# Create your models here.
VIA_EMAIL="via_email"
VIA_FACEBOOK="via_facebook"

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        abstract = True


class UserManager(AbstractUserManager):
    def _create_user(
            self,
            email=None,
            username=None,
            facebook=None,
            password=None,
            is_super_user=False,
            **extra_fields,
    ):
        """
        Create and save a user with the given phone and password.
        """
        if is_super_user:
            user = self.model(username=username, **extra_fields)
            user.password = make_password(password)
            user.save(using=self._db)
            return user

        if facebook is None and email is None:
            raise ValueError("The given facebook or email must be set")
        if email:
            user = self.model(email=email, **extra_fields)
        else:
            user = self.model(facebook=facebook, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, email=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(
            username=username, password=password, is_super_user=True, **extra_fields
        )

    def create_user(self, facebook=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        if email:
            return self._create_user(email=email, password=password, **extra_fields)
        elif facebook:
            return self._create_user(facebook=facebook, password=password, **extra_fields)


class User(AbstractUser, BaseModel):
    AUTH_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_FACEBOOK, VIA_FACEBOOK),
    )
    email = models.EmailField(null=True, verbose_name="Email", blank=True)
    facebook = models.CharField(null=True, blank=True, verbose_name="Facebook", max_length=256)
    auth_type = models.CharField(max_length=50, choices=AUTH_TYPE, default="via_email")

    objects = UserManager()

    def __str__(self):
        return self.email if self.email is not None else self.facebook

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh.token)
        }