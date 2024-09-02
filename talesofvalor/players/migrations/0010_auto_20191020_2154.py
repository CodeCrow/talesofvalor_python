# Generated by Django 2.1.9 on 2019-10-21 01:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_auto_20191020_2154'),
        ('players', '0009_auto_20190915_0919'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='car_registration',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
        migrations.AddField(
            model_name='registrationrequest',
            name='car_registration',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
        migrations.AddField(
            model_name='registrationrequest',
            name='event_registration_item',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='events.EventRegistrationItem'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registrationrequest',
            name='mealplan_flag',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='registrationrequest',
            name='notes',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='registrationrequest',
            name='player',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='players.Player'),
            preserve_default=False,
        ),
    ]
