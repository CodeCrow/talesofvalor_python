# Generated by Django 3.2.12 on 2022-04-24 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_auto_20220410_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='bgs_due_date',
            field=models.DateField(default='04/24/2022'),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_date',
            field=models.DateField(default='04/24/2022'),
        ),
        migrations.AlterField(
            model_name='event',
            name='pel_due_date',
            field=models.DateField(default='04/24/2022'),
        ),
    ]
