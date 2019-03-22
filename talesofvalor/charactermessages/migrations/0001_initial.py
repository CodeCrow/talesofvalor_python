# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2019-03-22 01:07
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0003_auto_20180317_2321'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('characters', '0005_auto_20190321_2107'),
    ]

    operations = [
        migrations.CreateModel(
            name='CharacterMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', djangocms_text_ckeditor.fields.HTMLField(blank=True, default=b'')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date published')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='characters.Character')),
                ('created_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='charactermessages_charactermessage_author', to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
                ('modified_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='charactermessages_charactermessage_updater', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
