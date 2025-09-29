from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
import bcrypt
import uuid
from django.utils import timezone

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class BusinessElement(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    
    def get_by_natural_key(self, email):
        return self.get(email__iexact=email)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL)

    def set_password(self, raw_password: str):
        hashed = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt())
        self.password_hash = hashed.decode()

    def check_password(self, raw_password: str) -> bool:
        try:
            return bcrypt.checkpw(raw_password.encode(), self.password_hash.encode())
        except Exception:
            return False

    def __str__(self):
        return f"{self.email}"


class AccessRule(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE)

    read = models.BooleanField(default=False)
    read_all = models.BooleanField(default=False)
    create = models.BooleanField(default=False)
    update = models.BooleanField(default=False)
    update_all = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    delete_all = models.BooleanField(default=False)

    class Meta:
        unique_together = ("role", "element")


class SessionToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def expire(self):
        self.is_active = False
        self.expired_at = timezone.now()
        self.save()
