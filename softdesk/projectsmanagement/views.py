from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, serializers
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import Project, Issue, Comment, ProjectContributor
from .serializers import ProjectSerializer, ProjectListSerializer, IssueSerializer, CommentSerializer
from .permissions import IsProjectContributor, IsAuthorOrReadOnly
from .utils import get_viewable_projects, check_contributors


class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == "retrieve" and self.detail_serializer_class is not None:
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
        }
        return permission_classes.get(self.action, [IsAuthenticated()])

    def create(self, validated_data):
        contributors_data = self.initial_data.get("contributors", [])
        request = self.context.get("request")
        if not request or not request.user:
            raise serializers.ValidationError("User must be authenticated.")

        validated_data["author"] = request.user
        project = Project.objects.create(**validated_data)
        ProjectContributor.objects.create(project=project, user=request.user)

        for username in contributors_data:
            user = get_user_model().objects.get(username=username)
            ProjectContributor.objects.create(project=project, user=user)

        return project

    @action(detail=True, methods=["post"], permission_classes=[IsAuthorOrReadOnly])
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
            return Response({"error": "No contributors provided."}, status=status.HTTP_400_BAD_REQUEST)

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
            {"message": "Contributors added successfully.", "added_contributors": added_users},
            status=status.HTTP_200_OK,
        )


class IssueViewSet(ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        """
        Return only issues that belong to projects where the user is a contributor.
        """
        user = self.request.user
        projects_list = get_viewable_projects(user)
        return Issue.objects.filter(project__in=projects_list)

    def validate_assignee(self, value):
        """Ensure the assignee is a contributor of the project's issue."""
        project = self.instance.project if self.instance else self.initial_data.get("project")

        if not project:
            raise serializers.ValidationError("Vous devez spécifier un projet auquel l'issue est rattachée.")

        if isinstance(project, int) or isinstance(project, str):
            try:
                project = Project.objects.get(id=project)
            except Project.DoesNotExist:
                raise serializers.ValidationError("Le projet n'existe pas.")

        contributors_list = check_contributors(project)
        if value not in contributors_list:
            raise serializers.ValidationError("L'assignee doit être un contributeur du projet.")

        return value

    def create(self, validated_data):
        request = self.context.get("request")
        project = validated_data["project"]
        project_author = project.author
        contributors_list = check_contributors(project)

        if not request or (request.user not in contributors_list and request.user != project_author):
            raise serializers.ValidationError("Seul l'auteur et les contributeurs du projet peuvent créer des issues.")
        validated_data["author"] = request.user
        return super().create(validated_data)

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
                {"detail": "Only the assignee or the author can update the status."}, status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get("status", None)

        if new_status not in dict(Issue.STATUS_CHOICES):
            return Response(
                {"detail": "Invalid status. Choose from: TODO, IN_PROGRESS, FINISHED."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        issue.status = new_status
        issue.save()

        return Response({"status": issue.status}, status=status.HTTP_200_OK)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        """
        Return only comments that belong to issues in projects where the user is a contributor.
        """
        user = self.request.user
        projects_list = get_viewable_projects(user)
        viewable_issues = Issue.objects.filter(project__in=projects_list)

        return Comment.objects.filter(issue__in=viewable_issues)

    def create(self, validated_data):
        request = self.context.get("request")
        issue = validated_data["issue"]
        project = issue.project
        contributors_list = check_contributors(project)

        if not request or request.user not in contributors_list:
            raise serializers.ValidationError("Seul l'auteur et les contributeurs du projet peuvent créer des issues.")
        validated_data["author"] = request.user
        return super().create(validated_data)
