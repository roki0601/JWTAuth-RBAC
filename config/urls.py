from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('api/auth/', include('modules.users.urls')),
    path('api/business/', include('modules.bus_logic.urls')),
    path('admin/', admin.site.urls),
]