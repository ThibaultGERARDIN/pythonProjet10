from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import Project, Issue, Comment, ProjectContributor
from .serializers import ProjectSerializer, IssueSerializer, CommentSerializer
from .permissions import IsProjectContributor, IsAuthorOrReadOnly


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsProjectContributor]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        if request.user != project.author:
            return Response(
                {"detail": "Vous n'avez pas le droit de modifier ce projet."}, status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["post"], permission_classes=[IsProjectContributor])
    def add_contributors(self, request, pk=None):
        """
        Custom action to add contributors to an existing project.
        Request format:
        {
            "contributors": ["username1", "username2"]
        }
        """
        project = self.get_object()

        # Get contributor usernames from request data
        contributor_usernames = request.data.get("contributors", [])

        if not contributor_usernames:
            return Response({"error": "No contributors provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve users and add them as contributors
        added_users = []
        for username in contributor_usernames:
            try:
                user = get_user_model().objects.get(username=username)
                # Check if the user is already a contributor
                if not ProjectContributor.objects.filter(project=project, user=user).exists():
                    ProjectContributor.objects.create(project=project, user=user)
                    added_users.append(username)
            except get_user_model().DoesNotExist:
                return Response({"error": f"User '{username}' does not exist."}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {"message": "Contributors added successfully.", "added_contributors": added_users},
            status=status.HTTP_200_OK,
        )


class IssueViewSet(ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
