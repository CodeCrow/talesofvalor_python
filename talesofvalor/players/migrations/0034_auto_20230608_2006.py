# Generated by Django 3.2.17 on 2023-06-09 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0033_alter_player_player_pronouns'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='registration_type',
            field=models.CharField(choices=[('cast', 'Cast'), ('player', 'Player')], default='player', max_length=10),
        ),
        migrations.AlterField(
            model_name='registrationrequest',
            name='status',
            field=models.TextField(choices=[('requested', 'Requested'), ('pending', 'Pending'), ('complete', 'Complete'), ('denied', 'Denied')], default='requested', help_text='Status of the request in ToV system.'),
        ),
        migrations.AlterModelOptions(
            name='registration',
            options={'permissions': (('register_as_cast', 'Can register as cast'), )},
        )
    ]
    