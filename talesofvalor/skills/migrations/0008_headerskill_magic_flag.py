# Generated by Django 3.0.11 on 2021-06-23 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0007_header_open_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='headerskill',
            name='magic_flag',
            field=models.BooleanField(default=False, help_text='\n            Indicates that this skill is magical.\n            ', verbose_name='Is this magical?'),
        ),
    ]
