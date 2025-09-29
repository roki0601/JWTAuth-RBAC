from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import jwt
from modules.users.models import User

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/admin/'):
            return None
        auth = request.META.get('HTTP_AUTHORIZATION')
        if not auth:
            request.user = None
            return
        parts = auth.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            request.user = None
            return
        token = parts[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get('user_id')
            user = User.objects.filter(id=user_id, is_active=True).first()
            request.user = user
        except jwt.ExpiredSignatureError:
            request.user = None
        except Exception:
            request.user = None
