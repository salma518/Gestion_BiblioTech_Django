from django.contrib.auth.backends import BaseBackend
from .models import Utilisateur

class AuthUtilisateur(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = Utilisateur.objects.get(email=username)
            if user.check_password(password):
                return user
        except Utilisateur.DoesNotExist:
            return None
    def get_user(self,user_id):
        try:
            return Utilisateur.objects.get(id=user_id)
        except Utilisateur.DoesNotExist:
            return None
