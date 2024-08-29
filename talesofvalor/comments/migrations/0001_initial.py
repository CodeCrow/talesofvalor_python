# Generated by Django 3.0.11 on 2022-01-09 19:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('comment', djangocms_text_ckeditor.fields.HTMLField()),
                ('object_id', models.PositiveIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date published')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('content_type', models.ForeignKey(limit_choices_to=models.Q(models.Q(('app_label', 'characters'), ('model', 'Character')), models.Q(('app_label', 'events'), ('model', 'Event')), models.Q(('app_label', 'attendance'), ('model', 'Attendance')), models.Q(('app_label', 'betweengameabilities'), ('model', 'betweengameability')), models.Q(('app_label', 'origins'), ('model', 'Origin')), models.Q(('app_label', 'players'), ('model', 'Player')), models.Q(('app_label', 'skills'), ('model', 'Header')), models.Q(('app_label', 'skills'), ('model', 'Skill')), _connector='OR'), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments_comment_author', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments_comment_updater', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
