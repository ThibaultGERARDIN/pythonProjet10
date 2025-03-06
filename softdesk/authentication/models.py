from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self, username, date_of_birth, rgpd_consent, password=None, **extra_fields):
        user = self.model(username=username, date_of_birth=date_of_birth, rgpd_consent=rgpd_consent)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, date_of_birth, rgpd_consent, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, date_of_birth, rgpd_consent, password, **extra_fields)


class MyUser(AbstractUser):

    date_of_birth = models.DateField(verbose_name="Date de naissance")
    can_be_contacted = models.BooleanField(default=False, verbose_name="J'accepte d'être contacté.")
    can_data_be_shared = models.BooleanField(default=False, verbose_name="J'accepte de partager mes données.")
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["date_of_birth", "can_be_contacted", "can_data_be_shared"]

    @property
    def age(self):
        today = timezone.now().date()
        age = int(
            today.year
            - (self.date_of_birth.year)
            - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )
        return age

    def __str__(self):
        return self.username
