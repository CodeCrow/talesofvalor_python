# Generated by Django 2.2.12 on 2020-06-28 21:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0006_auto_20200628_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prerequisite',
            name='origin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='origins.Origin'),
        ),
    ]
