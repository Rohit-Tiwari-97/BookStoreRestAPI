from django.contrib.auth.models import BaseUserManager


class MyUserManager(BaseUserManager):

    def create_user(self, email, created_at, userRole, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            created_at=created_at,
            userRole=userRole
            
        )

        user.set_password(password)
        user.save(using=self._db)

        return user



    def create_superuser(self, email, userRole = 'Admin', password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password,
            userRole
        )
        user.is_admin = True
        user.save(using=self._db)
        return user