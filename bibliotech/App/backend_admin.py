from django.contrib.auth.backends import BaseBackend
from .models import Admin

class AuthAdmin(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = Admin.objects.get(email=username)
            if user.check_password(password):
                return user
        except Admin.DoesNotExist:
            return None
    def get_user(self,user_id):
        try:
            return Admin.objects.get(id=user_id)
        except Admin.DoesNotExist:
            return None
