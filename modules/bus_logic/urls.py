from django.urls import path
from .views import ProductsView, OrdersView

urlpatterns = [
    path('products/', ProductsView.as_view()),
    path('orders/', OrdersView.as_view()),
]
