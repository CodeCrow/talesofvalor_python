# Generated by Django 2.2.12 on 2020-06-28 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0005_auto_20200628_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rule',
            name='new_cost',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
