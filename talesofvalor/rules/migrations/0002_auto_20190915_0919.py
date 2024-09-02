# Generated by Django 2.1.9 on 2019-09-15 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rule',
            name='content_type',
            field=models.ForeignKey(limit_choices_to=models.Q(models.Q(('app_label', 'origins'), ('model', 'Origin')), models.Q(('app_label', 'skills'), ('model', 'Header')), models.Q(('app_label', 'skills'), ('model', 'Skill')), _connector='OR'), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
    ]
