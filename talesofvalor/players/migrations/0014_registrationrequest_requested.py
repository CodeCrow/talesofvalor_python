# Generated by Django 2.1.9 on 2020-02-11 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0013_auto_20200211_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationrequest',
            name='requested',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='date created'),
        ),
    ]
