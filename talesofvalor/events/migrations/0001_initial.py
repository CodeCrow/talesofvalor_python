# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('event_date', models.DateField(default=datetime.date.today)),
                ('pel_due_date', models.DateField(default=datetime.date.today)),
                ('bgs_due_date', models.DateField(default=datetime.date.today)),
                ('oog_p', models.BooleanField(default=False)),
                ('bgs_p', models.BooleanField(default=False)),
                ('notes', djangocms_text_ckeditor.fields.HTMLField(default=b'', blank=True)),
                ('summary', djangocms_text_ckeditor.fields.HTMLField(default=b'', blank=True)),
            ],
        ),
    ]
