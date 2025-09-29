from rest_framework.views import APIView
from rest_framework.response import Response
from modules.users.permissions import RoleBasedPermission

class ProductsView(APIView):
    permission_classes = []

    def get(self, request):
        data = [
            {'id': 1, 'name': 'Product A'},
            {'id': 2, 'name': 'Product B'},
        ]
        return Response(data)

class OrdersView(APIView):
    permission_classes = [RoleBasedPermission]
    element_name = 'orders'
    action = 'read'

    def get(self, request):
        return Response([
            {'id': 1, 'owner': str(request.user.id) if request.user else None, 'items': []}
        ])
