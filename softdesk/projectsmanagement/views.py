from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import Project, Issue, Comment, ProjectContributor
from .serializers import (
    ProjectSerializer,
    ProjectListSerializer,
    IssueSerializer,
    IssueListSerializer,
    CommentListSerializer,
    CommentSerializer,
)
from .permissions import IsProjectContributor, IsAuthorOrReadOnly
from .utils import get_viewable_projects, check_contributors


class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        # Use the detailed serializer for retrieving, creating, or updating projects
        if self.action in ["retrieve", "create", "update", "partial_update"] and self.detail_serializer_class:
            return self.detail_serializer_class
        return super().get_serializer_class()


class ProjectViewSet(MultipleSerializerMixin, ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectSerializer

    def get_permissions(self):

        permission_classes = {
            "retrieve": [IsProjectContributor()],
            "update": [IsAuthorOrReadOnly()],
            "destroy": [IsAuthorOrReadOnly()],
            "partial_update": [IsAuthorOrReadOnly()],
            "add_contributors": [IsAuthorOrReadOnly()],
            "remove_contributors": [IsAuthorOrReadOnly()],
        }
        return permission_classes.get(self.action, [IsAuthenticated()])

    def create(self, request, *args, **kwargs):
        """
        Request format:
        {
            "name": "projectname",
            "description": "Description of the project",
            "type": "BACK_END / FRONT_END / IOS / ANDROID",
            "contributors": ["username1", "username2"]
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        contributors_data = request.data.get("contributors", [])
        user = request.user

        if not user or not user.is_authenticated:
            return Response({"error": "Vous devez être authentifié."}, status=status.HTTP_403_FORBIDDEN)

        # Save project with the validated data, setting the author correctly
        project = serializer.save(author=user)

        # Add the author as a contributor
        ProjectContributor.objects.create(project=project, user=user)

        # Add additional contributors
        added_users = []
        for username in contributors_data:
            try:
                contributor = get_user_model().objects.get(username=username)
                if not ProjectContributor.objects.filter(project=project, user=contributor).exists():
                    ProjectContributor.objects.create(project=project, user=contributor)
                    added_users.append(username)
            except get_user_model().DoesNotExist:
                return Response(
                    {"error": f"L'utilisateur '{username}' n'existe pas."}, status=status.HTTP_404_NOT_FOUND
                )

        return Response(
            {
                "message": "Le projet a bien été créé",
                "project": ProjectSerializer(project).data,
                "added_contributors": added_users,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def add_contributors(self, request, pk=None):
        """
        Custom action to add contributors to an existing project.
        Request format:
        {
            "contributors": ["username1", "username2"]
        }
        """
        project = self.get_object()

        contributor_usernames = request.data.get("contributors", [])

        if not contributor_usernames:
            return Response({"error": "Vous n'avez pas fourni d'utilisateur."}, status=status.HTTP_400_BAD_REQUEST)

        added_users = []
        for username in contributor_usernames:
            try:
                user = get_user_model().objects.get(username=username)
                if not ProjectContributor.objects.filter(project=project, user=user).exists():
                    ProjectContributor.objects.create(project=project, user=user)
                    added_users.append(username)
            except get_user_model().DoesNotExist:
                return Response({"error": f"User '{username}' does not exist."}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {"message": "Contributeur(s) ajouté(s) avec succès.", "added_contributors": added_users},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def remove_contributors(self, request, pk=None):
        """
        Custom action to remove contributors from an existing project.
        Request format:
        {
            "contributors": ["username1", "username2"]
        }
        """
        project = self.get_object()

        contributor_usernames = request.data.get("contributors", [])

        if not contributor_usernames:
            return Response({"error": "Vous n'avez pas fourni d'utilisateur."}, status=status.HTTP_400_BAD_REQUEST)

        removed_users = []
        for username in contributor_usernames:
            try:
                user = get_user_model().objects.get(username=username)
                contributor = ProjectContributor.objects.filter(project=project, user=user)

                if contributor.exists():
                    contributor.delete()
                    removed_users.append(username)
                else:
                    return Response(
                        {"error": f"L'utilisateur '{username}' n'est pas un contributeur."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            except get_user_model().DoesNotExist:
                return Response(
                    {"error": f"L'utilisateur '{username}' n'existe pas."}, status=status.HTTP_404_NOT_FOUND
                )

        return Response(
            {"message": "Le(s) contributeur(s) ont été retiré(s) du projet.", "removed_contributors": removed_users},
            status=status.HTTP_200_OK,
        )


class IssueViewSet(MultipleSerializerMixin, ModelViewSet):
    serializer_class = IssueListSerializer
    detail_serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        """
        Return only issues that belong to projects where the user is a contributor.
        """
        user = self.request.user
        projects_list = get_viewable_projects(user)
        return Issue.objects.filter(project__in=projects_list)

    def create(self, request, *args, **kwargs):
        """
        Ensure only the project author and contributors can create issues.
        Request format:
        {
            "title": "issue title",
            "description": "Description of the issue",
            "project": ID of related project (int)
            "status": "TODO" / "IN_PROGRESS" / "DONE",
            "priority": "LOW" / "MEDIUM" / "HIGH",
            "tag": "BUG" / "TASK" / "FEATURE",
            "assignee": "username"
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = serializer.validated_data["project"]
        user = request.user
        contributors_list = check_contributors(project)

        if user not in contributors_list and user != project.author:
            return Response(
                {"detail": "Seuls l'auteur ou les contributeurs du projet peuvent créer des issues."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer.save(author=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        """
        Custom action to allow only the assignee and author to update the issue status.
        """
        try:
            issue = self.get_object()
        except Issue.DoesNotExist:
            return Response({"detail": "Issue not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user not in [issue.assignee, issue.author]:
            return Response(
                {"detail": "Seuls l'assignee ou l'auteur peuvent modifier le status."}, status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get("status", None)

        if new_status not in dict(Issue.STATUS_CHOICES):
            return Response(
                {"detail": "Status invalide. Choisissez parmis: TODO, IN_PROGRESS, DONE."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        issue.status = new_status
        issue.save()

        return Response({"status": issue.status}, status=status.HTTP_200_OK)


class CommentViewSet(MultipleSerializerMixin, ModelViewSet):
    serializer_class = CommentListSerializer
    detail_serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        """
        Return only comments that belong to issues in projects where the user is a contributor.
        """
        user = self.request.user
        projects_list = get_viewable_projects(user)
        viewable_issues = Issue.objects.filter(project__in=projects_list)

        return Comment.objects.filter(issue__in=viewable_issues)

    def create(self, request, *args, **kwargs):
        """
        Ensure only the project author and contributors can create comments.

        Request format:
        {
            "content": "Content of the comment",
            "issue": ID of related issue (int)
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        issue = serializer.validated_data["issue"]
        project = issue.project
        contributors_list = check_contributors(project)

        if request.user not in contributors_list:
            return Response(
                {"detail": "Seuls l'auteur ou les contributeurs du projet peuvent créer des commentaires."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
