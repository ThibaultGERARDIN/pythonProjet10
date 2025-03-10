from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import MyUser
from .serializers import UserSerializer, UserDetailSerializer
from .serializers import RegisterSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == "retrieve" and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class RegisterView(generics.CreateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class UserViewSet(MultipleSerializerMixin, ReadOnlyModelViewSet):

    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    detail_serializer_class = UserDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        if user.can_data_be_shared is not True:
            return Response(
                {"detail": "Cet utilisateur ne souhaite pas partager ses informations"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().retrieve(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user != user:
            return Response(
                {"detail": "Vous n'avez pas le droit de modifier cet utilisateur."}, status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user != user:
            return Response(
                {"detail": "Vous n'avez pas le droit de supprimer cet utilisateur."}, status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
