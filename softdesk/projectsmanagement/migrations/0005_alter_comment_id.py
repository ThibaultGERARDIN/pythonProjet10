# Generated by Django 5.1.6 on 2025-03-07 15:00

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectsmanagement', '0004_issue_author_project_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
