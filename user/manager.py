from django.contrib.auth.models import BaseUserManager


class MyUserManager(BaseUserManager):

    def create_user(self, email, password=None, userRole='Customer'):
        
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            userRole = userRole
        )

        user.set_password(password)
        user.save(using=self._db)

        return user



    def create_superuser(self, email, password=None, userRole='Admin'):

        user = self.create_user(
            email,
            password,
            userRole,
        )
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user