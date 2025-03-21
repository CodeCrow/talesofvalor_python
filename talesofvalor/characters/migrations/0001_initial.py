# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0007_auto_20161016_1055'),
        ('players', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'alive', max_length=50, choices=[(b'alive', b'Alive'), (b'dead', b'Dead')])),
                ('name', models.CharField(max_length=255, verbose_name='Character Name')),
                ('description', models.TextField(blank=True)),
                ('history', models.TextField(blank=True)),
                ('player_notes', models.TextField(blank=True)),
                ('staff_notes_visible', models.TextField(blank=True)),
                ('staff_notes_hidden', models.TextField(blank=True)),
                ('staff_attention_flag', models.BooleanField(default=False)),
                ('npc_flag', models.BooleanField(default=False)),
                ('active_flag', models.BooleanField(default=False)),
                ('cp_spent', models.PositiveIntegerField(default=0)),
                ('cp_available', models.PositiveIntegerField(default=0)),
                ('cp_transferred', models.PositiveIntegerField(default=0)),
                ('picture', filer.fields.image.FilerImageField(blank=True, to='filer.Image', null=True, on_delete=models.SET_NULL)),
                ('player', models.ForeignKey(to='players.Player', on_delete=models.CASCADE)),
            ],
        ),
    ]
