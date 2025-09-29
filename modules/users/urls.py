from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, MeView, SoftDeleteView,
    RefreshView, RoleListCreate, AccessRuleListCreate, BusinessElementListCreate
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('refresh/', RefreshView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('me/', MeView.as_view()),
    path('delete/', SoftDeleteView.as_view()),

    path('roles/', RoleListCreate.as_view()),
    path('access-rules/', AccessRuleListCreate.as_view()),
    path('elements/', BusinessElementListCreate.as_view()),
]
