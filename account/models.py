from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# THINGS TO UNDERSTAND !!!
# Django implicitly creates the objects attribute as an instance of Manager. 
# Behind the scenes, it's equivalent to:from django.db import models

# class Manager(models.Manager):
#     pass

# class MyModel(models.Model):
#     name = models.CharField(max_length=100)

#     objects = Manager()

# We will use AbstractBaseUser to make our own model.
# We will use BaseUserManager to make user manager.

# Custom User Manager

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, password2=None):
        """Creates and saves the NORMAL user with the given email, name and password"""

        if not email:
            raise ValueError('User must have an email address')

        """Not nessary for name to normalize"""
        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )
        """Hashed password is saved"""
        user.set_password(password)
        user.save(using=self._db)
        return user

    # To use this method. i.e custome super user we have to add AUTH_USER_MODEL = 'accounts.User
    def create_superuser(self, email, name, password=None):
        if not email:
            raise ValidationError('User must have email address')
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            name=name,
        )
        """We will set it to true"""
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        max_length=255, verbose_name='email', unique=True)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    is_varified = models.BooleanField(default = False)
    otp = models.IntegerField(null=True)
    updated_at = models.DateField(auto_now=True)

    # this manager will be used to create, retrieve, update, and delete instances of the model.
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    # If we dont write this, we will see object(1) object(2) object(3) and so on.
    def __str__(self):
        # __str__ is a special method that is supposed to return a string representation of and object.
        # return '{}'.format(self.email)
        return self.email

    def has_perm(self, perm, obj=None):
        "Does this user have a specific permission?"
        # return True This gives permission to common user
        """This gives permission to admin only"""
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does this user have permission to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user the member of staff?"
        return self.is_admin


