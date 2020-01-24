# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

def load_initial_groups_from_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command("loaddata", "initial_groups")

class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cp_available', models.PositiveIntegerField(default=0)),
                ('game_started', models.ForeignKey(to='events.Event', null=True, on_delete=models.SET_NULL)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),

        migrations.RunPython(load_initial_groups_from_fixture),
    ]
