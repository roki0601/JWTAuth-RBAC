from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
import jwt
import datetime
from .models import User, SessionToken, Role, BusinessElement, AccessRule
from .serializers import UserRegisterSerializer, UserSerializer, RoleSerializer, BusinessElementSerializer, AccessRuleSerializer
import secrets

def generate_jwt(user_id: str):
    payload = {
        'user_id': str(user_id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=int(settings.JWT_EXP_SECONDS)),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    # pyjwt returns str in py3.11, ensure str
    if isinstance(token, bytes):
        token = token.decode()
    return token

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active or not user.check_password(password):
            return Response({'detail': 'invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        access = generate_jwt(user.id)
        refresh = secrets.token_urlsafe(32)
        SessionToken.objects.create(token=refresh, user=user)

        return Response({'access': access, 'refresh': refresh})

class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response({'detail': 'refresh token required'}, status=status.HTTP_400_BAD_REQUEST)

        st = SessionToken.objects.filter(token=refresh, is_active=True).first()
        if not st:
            return Response({'detail': 'invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

        if st.expired_at and st.expired_at <= datetime.datetime.utcnow():
            st.expire()
            return Response({'detail': 'refresh token expired'}, status=status.HTTP_401_UNAUTHORIZED)

        access = generate_jwt(st.user.id)
        return Response({'access': access})

class LogoutView(APIView):
    def post(self, request):
        user = getattr(request, 'user', None)
        if not user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        SessionToken.objects.filter(user=user, is_active=True).update(is_active=False)
        return Response({'detail': 'logged out'})

class MeView(APIView):
    def get(self, request):
        user = getattr(request, 'user', None)
        if not user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(UserSerializer(user).data)

    def patch(self, request):
        user = getattr(request, 'user', None)
        if not user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class SoftDeleteView(APIView):
    def post(self, request):
        user = getattr(request, 'user', None)
        if not user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user.is_active = False
        user.save()
        SessionToken.objects.filter(user=user, is_active=True).update(is_active=False)
        return Response({'detail': 'account marked as inactive'})

# Админские CRUD для ролей/прав (упрощённые)
class RoleListCreate(APIView):
    def get(self, request):
        # только админ
        if not request.user or request.user.role is None or request.user.role.name != 'admin':
            return Response(status=status.HTTP_403_FORBIDDEN)
        data = RoleSerializer(Role.objects.all(), many=True).data
        return Response(data)

    def post(self, request):
        if not request.user or request.user.role is None or request.user.role.name != 'admin':
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AccessRuleListCreate(APIView):
    def get(self, request):
        if not request.user or request.user.role is None or request.user.role.name != 'admin':
            return Response(status=status.HTTP_403_FORBIDDEN)
        data = AccessRuleSerializer(AccessRule.objects.all(), many=True).data
        return Response(data)

    def post(self, request):
        if not request.user or request.user.role is None or request.user.role.name != 'admin':
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = AccessRuleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BusinessElementListCreate(APIView):
    def get(self, request):
        data = BusinessElementSerializer(BusinessElement.objects.all(), many=True).data
        return Response(data)

    def post(self, request):
        if not request.user or request.user.role is None or request.user.role.name != 'admin':
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = BusinessElementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
