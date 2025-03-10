from .models import Project, Issue, Comment, ProjectContributor
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .utils import check_contributors


class ProjectContributorSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", queryset=get_user_model().objects.all())

    class Meta:
        model = ProjectContributor
        fields = ["user"]


class CommentListSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all())

    class Meta:
        model = Comment
        fields = ["id", "issue", "author"]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all())

    class Meta:
        model = Comment
        fields = ["id", "issue", "author", "content", "created_at"]


class IssueListSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    assignee = serializers.SlugRelatedField(
        slug_field="username", queryset=get_user_model().objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "author",
            "assignee",
            "priority",
        ]


class IssueSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    assignee = serializers.SlugRelatedField(
        slug_field="username", queryset=get_user_model().objects.all(), required=False, allow_null=True
    )
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "project",
            "author",
            "assignee",
            "priority",
            "tag",
            "status",
            "created_at",
        ]

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


class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    contributors = serializers.SerializerMethodField()
    issues = IssueListSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "type", "description", "author", "contributors", "created_at", "issues"]

    def get_contributors(self, obj):
        """
        Returns a list of contributor usernames.
        """
        return [contributor.user.username for contributor in obj.contributors.all()]


class ProjectListSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    contributors = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ["id", "name", "author", "contributors"]

    def get_contributors(self, obj):
        """
        Returns a list of contributor usernames.
        """
        return [contributor.user.username for contributor in obj.contributors.all()]
