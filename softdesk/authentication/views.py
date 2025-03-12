from rest_framework.viewsets import ModelViewSet
from .models import MyUser
from .serializers import UserSerializer, UserDetailSerializer
from .serializers import RegisterSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsSelfOrReadOnly
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import action


class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == "retrieve" and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class RegisterView(generics.CreateAPIView):
    """Request format:
    {
        "username": "username",
        "password1": "password",
        "password2": "password",
        "date_of_birth": "TYYY/MM/DD",
        "can_be_contacted": "True" or "False", (false by default)
        "can_data_be_shared": "True" or "False" (false by default)
    }
    """

    queryset = MyUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class UserViewSet(MultipleSerializerMixin, ModelViewSet):

    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    detail_serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated, IsSelfOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user == user:
            return super().retrieve(self, request, *args, **kwargs)
        elif user.can_data_be_shared is not True:
            return Response(
                {"detail": "Cet utilisateur ne souhaite pas partager ses informations"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().retrieve(self, request, *args, **kwargs)

    @action(detail=True, methods=["post"], permission_classes=[IsSelfOrReadOnly])
    def change_password(self, request, pk=None):
        """
        Custom action to allow users to change their password.
        Request format:
        {
            "old_password": "currentpassword",
            "new_password": "newsecurepassword"
        }
        """
        user = self.get_object()

        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response(
                {"detail": "Veuillez fournir l'ancien et le nouveau mot de passe."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not check_password(old_password, user.password):
            return Response(
                {"detail": "L'ancien mot de passe est incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"detail": "Mot de passe mis à jour avec succès."},
            status=status.HTTP_200_OK,
        )
