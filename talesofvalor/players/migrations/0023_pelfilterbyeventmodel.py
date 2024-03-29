# Generated by Django 3.2.11 on 2022-01-29 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0022_auto_20220123_1750'),
    ]

    operations = [
        migrations.CreateModel(
            name='PELFilterByEventModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_selector', models.CharField(choices=[('Spring 1, 2019', 'Spring 1 2019 - 05-01-2019'), ('Spring 2, 2019', 'Spring 2 2019 - 06-02-2019'), ('Fall 1, 2019', 'Fall 1 2019 - 09-03-2019'), ('Fall 2, 2019', 'Fall 2 2019 - 10-04-2019'), ('Spring 1, 2020', 'Spring 1 2020 - 05-08-2020')], max_length=20)),
            ],
        ),
    ]
