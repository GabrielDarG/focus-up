# home/backends.py

from django.contrib.auth.backends import ModelBackend
from .models import Usuario

class EmailOrUsernameBackend(ModelBackend):
   
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            if '@' in username:
                user = Usuario.objects.get(email__iexact=username)
            else:
                user = Usuario.objects.get(nome_usuario__iexact=username)
        except Usuario.DoesNotExist:
            return None

        if user.check_password(password):
            return user 
        
        return None 

    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None