# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

def load_initial_groups_from_fixture(apps, schema_editor):
    from django.core.management import call_command
    from django.contrib.auth.models import Group
    from django.db.models import signals

    from cms.signals.permissions import pre_save_group, post_save_user_group

    # django-cms clears its menu cache whenever a Group is saved, but this
    # migration runs before the cms tables exist on a database built from
    # scratch (a test database, or a brand new environment), so that clear
    # blows up.  Nothing can be stale before there is any data, so take those
    # receivers off while the fixture loads and put them back afterwards.
    signals.pre_save.disconnect(sender=Group, dispatch_uid='cms_pre_save_group')
    signals.post_save.disconnect(sender=Group, dispatch_uid='cms_post_save_group')
    try:
        call_command("loaddata", "initial_groups")
    finally:
        signals.pre_save.connect(
            pre_save_group, sender=Group, dispatch_uid='cms_pre_save_group')
        signals.post_save.connect(
            post_save_user_group, sender=Group, dispatch_uid='cms_post_save_group')

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
