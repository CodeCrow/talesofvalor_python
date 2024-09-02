# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-15 18:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20170530_2045'),
        ('players', '0002_pel'),
    ]

    operations = [
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cabin', models.CharField(blank=True, default=b'', help_text='What cabin is the player staying in?', max_length=100)),
                ('mealplan_flag', models.BooleanField(default=False, help_text='Has the player signed up for a meal plan.')),
                ('notes', models.TextField(blank=True, default=b'')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='players.Player')),
            ],
        ),
    ]
