import uuid
from django.db import models
from django.contrib.auth import get_user_model


class Project(models.Model):
    TYPE_CHOICES = [
        ("BACK_END", "Back-end"),
        ("FRONT_END", "Front-end"),
        ("IOS", "iOS"),
        ("ANDROID", "Android"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="owned_projects")
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)

    def __str__(self):
        return f"{self.id} - {self.name}"


class ProjectContributor(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="contributors")
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="projects_contributed_to")

    class Meta:
        unique_together = ("project", "user")

    def __str__(self):
        return f"{self.user.username} - {self.project.name}"


class Issue(models.Model):
    STATUS_CHOICES = [
        ("TODO", "To Do"),
        ("IN_PROGRESS", "In Progress"),
        ("DONE", "Done"),
    ]
    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]
    TAG_CHOICES = [
        ("BUG", "Bug"),
        ("TASK", "Task"),
        ("IMPROVEMENT", "Improvement"),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="issues")
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="created_issues")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="TODO")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="MEDIUM")
    assignee = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_issues"
    )
    tag = models.CharField(max_length=15, choices=TAG_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment {self.id} par {self.author.username} sur {self.issue.title}"
