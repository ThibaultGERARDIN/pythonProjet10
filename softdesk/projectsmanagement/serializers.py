from .models import Project, Issue, Comment, ProjectContributor
from rest_framework import serializers
from django.contrib.auth import get_user_model


class ProjectContributorSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", queryset=get_user_model().objects.all())

    class Meta:
        model = ProjectContributor
        fields = ["user"]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all())

    class Meta:
        model = Comment
        fields = ["id", "issue", "author", "content", "created_at"]


class IssueReducedSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    assignee = serializers.SlugRelatedField(
        slug_field="username", queryset=get_user_model().objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Issue
        fields = [
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


class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    contributors = serializers.SerializerMethodField()
    issues = IssueReducedSerializer(many=True, read_only=True)

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
