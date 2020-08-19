from .models import customUser
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class AuthenticationEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel= get_user_model()
        try:
            user= UserModel.objects.get(username = username)
        except UserModel.DoesNotExist:
            return None
        else:
            if getattr(user,'is_active',False) and user.check_password(password):
                return user
        return None
    
    def get_user(self,user_id):
        try:
            return customUser.objects.get(pk = user_id)
        except customUser.DoesNotExist:
            return None