from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self, username, date_of_birth, password=None, **extra_fields):
        user = self.model(username=username, date_of_birth=date_of_birth)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, date_of_birth, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, date_of_birth, password, **extra_fields)


class MyUser(AbstractUser):

    date_of_birth = models.DateField()
    rgpd_consent = models.BooleanField(default=False)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["date_of_birth", "rgpd_consent"]

    @property
    def age(self):
        today = timezone.now().date()
        age = int(
            today.year
            - (self.date_of_birth.year)
            - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )
        if age < 15:
            raise ValidationError("Vous devez avoir au moins 15ans pour vous inscrire.")
        else:
            return age

    def __str__(self):
        return self.username
