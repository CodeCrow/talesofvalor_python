# Generated by Django 3.2.15 on 2022-09-02 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0011_prerequisitegroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='rule',
            name='universal_flag',
            field=models.BooleanField(default=False, help_text='All characters get this.'),
        ),
    ]
