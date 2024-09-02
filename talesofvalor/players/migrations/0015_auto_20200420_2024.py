# Generated by Django 2.2.12 on 2020-04-21 00:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0014_registrationrequest_requested'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='local_contact',
            field=models.CharField(blank=True, default='', help_text='On site contact, such as a cell phone.', max_length=16),
        ),
        migrations.AddField(
            model_name='registration',
            name='vehicle_color',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
        migrations.AddField(
            model_name='registration',
            name='vehicle_make',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
        migrations.AddField(
            model_name='registration',
            name='vehicle_model',
            field=models.CharField(blank=True, default='', max_length=15),
        ),
        migrations.AddField(
            model_name='registration',
            name='vehicle_registration',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
    ]
