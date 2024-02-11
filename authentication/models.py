from django.db import models
from datetime import datetime, time
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.http import request

class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have a valid email address.')

        if not kwargs.get('username'):
            raise ValueError('Users must have a valid username.')

        account = self.model(
            email=self.normalize_email(email),
            username=kwargs.get('username'),
        )

        account.set_password(password)
        account.save(using=self._db)
        return account

    def create_superuser(self, email, password, **kwargs):
        """
        Creates and saves a superuser with the given email and password.
        """
        account = self.create_user(
            email,
            password=password,
            **kwargs
        )
        account.is_admin = True
        account.save(using=self._db)
        return account


class Account(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    fullname = models.CharField(max_length=255, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def get_full_name(self):
        # The user is identified by their email address
        return ' '.join([self.first_name,self.last_name])

    def get_abbreviated_name(self):
        first_name_letter = '*'
        first_lastname_letter = '*'
        try:
            first_name_letter = self.first_name[0]
            first_lastname_letter = self.last_name[0]
        except Exception:
            pass

        return "%s%s" % (first_name_letter, first_lastname_letter)

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
