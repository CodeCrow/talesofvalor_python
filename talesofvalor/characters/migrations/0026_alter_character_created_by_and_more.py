# Generated by Django 4.2.10 on 2024-02-10 17:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('characters', '0025_character_skills'),
    ]

    operations = [
        migrations.AlterField(
            model_name='character',
            name='created_by',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_author', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='character',
            name='modified_by',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updater', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='characterlog',
            name='created_by',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_author', to=settings.AUTH_USER_MODEL),
        ),
    ]