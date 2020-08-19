from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self,email,username,password,**extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        user = self.model(email=self.normalize_email(email),**extra_fields)
        user.set_password(password)
        user.username = username
        user.save()
        return user
    
    def create_superuser(self,email,username,password,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email,username, password, **extra_fields)