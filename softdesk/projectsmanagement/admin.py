from django.contrib import admin
from .models import Project, Issue, Comment, ProjectContributor


admin.site.register(ProjectContributor)
admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(Comment)
