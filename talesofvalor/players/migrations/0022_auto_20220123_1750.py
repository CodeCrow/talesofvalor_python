# Generated by Django 3.2.11 on 2022-01-23 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0021_auto_20220123_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pel',
            name='heavy_armor_worn_flag',
            field=models.BooleanField(default=False, verbose_name='Character wore heavy armor this event (cheaper Health pre-req)?'),
        ),
    ]
