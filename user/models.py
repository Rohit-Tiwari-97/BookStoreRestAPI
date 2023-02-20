from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .manager import MyUserManager
    


class MyUser(AbstractBaseUser):

    USER_ROLES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Author', 'Author'), 
        ('Customer', 'Customer'),
    ]

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    userRole = models.CharField(max_length=20,choices=USER_ROLES,default='Customer')
    is_active = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin



class MyUserProfile(models.Model):

    firstName = models.CharField(max_length=250)
    lastName = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    myuser = models.OneToOneField(MyUser, on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return f"{self.firstName} {self.lastName}"



class Books(models.Model):
    
    title = models.CharField(max_length=100)
    isbn = models.CharField(max_length=250,unique=True)
    description = models.TextField()
    publishDate = models.DateField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    author = models.ForeignKey(MyUser, on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return self.title

