# Generated by Django 3.0.11 on 2021-06-07 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0006_headerskill_capstone_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='header',
            name='open_flag',
            field=models.BooleanField(default=False, help_text="\n        Header is automatically 'open' without the need for purchase.\n        ", verbose_name='open?'),
        ),
    ]
