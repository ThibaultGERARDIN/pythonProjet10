from .models import Project, Issue, Comment, ProjectContributor
from rest_framework import serializers
from django.contrib.auth import get_user_model


class ProjectContributorSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", queryset=get_user_model().objects.all())

    class Meta:
        model = ProjectContributor
        fields = ["user"]


class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    contributors = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ["name", "type", "description", "author", "contributors"]

    def get_contributors(self, obj):
        """
        Returns a list of contributor usernames.
        """
        return [contributor.user.username for contributor in obj.contributors.all()]

    def create(self, validated_data):
        contributors_data = self.initial_data.get("contributors", [])
        request = self.context.get("request")
        author = request.user

        project = Project.objects.create(author=author, **validated_data)

        for username in contributors_data:
            user = get_user_model().objects.get(username=username)
            ProjectContributor.objects.create(project=project, user=user)

        return project


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

    def create(self, validated_data):
        request = self.context.get("request")
        if not request or request.user not in validated_data["project"].contributors.all():
            raise serializers.ValidationError("Only contributors can create issues.")
        validated_data["author"] = request.user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all())

    class Meta:
        model = Comment
        fields = ["id", "issue", "author", "description", "created_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        issue = validated_data["issue"]
        if not request or request.user not in issue.project.contributors.all():
            raise serializers.ValidationError("Only contributors can add comments.")
        validated_data["author"] = request.user
        return super().create(validated_data)
