# Generated by Django 5.1.6 on 2025-02-20 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_alter_myuser_managers_myuser_rgpd_consent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='date_of_birth',
            field=models.DateField(verbose_name='Date de naissance'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='rgpd_consent',
            field=models.BooleanField(default=False, verbose_name='Consentement partage de données'),
        ),
    ]
