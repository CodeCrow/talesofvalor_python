# Generated by Django 3.0.11 on 2021-07-07 01:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('rules', '0010_prerequisite_additional_header'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrerequisiteGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('operator', models.CharField(choices=[('OR', 'or'), ('AND', 'and')], default='OR', max_length=3)),
                ('content_type', models.ForeignKey(limit_choices_to=models.Q(models.Q(('app_label', 'origins'), ('model', 'Origin')), models.Q(('app_label', 'skills'), ('model', 'Header')), models.Q(('app_label', 'skills'), ('model', 'Skill')), _connector='OR'), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
    ]
