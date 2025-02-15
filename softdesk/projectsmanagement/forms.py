from django import forms
from .models import Project, Issue, Comment, Contributor


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ("name", "description", "contributors")


class ContributorForm(forms.ModelForm):
    class Meta:
        model = Contributor
        fields = ("user", "project", "role")


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ("title", "description", "project", "status", "priority", "assignee", "tag")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("issue", "author", "content")
