# Generated by Django 3.2.12 on 2022-02-27 14:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('origins', '0003_auto_20210727_1957'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='origin',
            name='skills',
        ),
        migrations.DeleteModel(
            name='OriginSkill',
        ),
    ]
