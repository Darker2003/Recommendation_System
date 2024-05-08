from .models import userdatabase
from django.contrib.auth.backends import ModelBackend

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = userdatabase.objects.get(email=email)
        except userdatabase.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user

    def get_user(self, user_id):
        try:
            return userdatabase.objects.get(pk=user_id)
        except userdatabase.DoesNotExist:
            return None