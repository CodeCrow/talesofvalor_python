# Generated by Django 3.2.17 on 2023-10-24 19:27

from django.db import migrations, models
import django.db.models.deletion
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('players', '0037_alter_registration_registration_request'),
        ('skills', '0012_alter_skill_options'),
        ('characters', '0024_alter_character_options'),
        ('events', '0009_alter_event_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='BetweenGameAbility',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.PositiveIntegerField()),
                ('question', djangocms_text_ckeditor.fields.HTMLField()),
                ('answer', djangocms_text_ckeditor.fields.HTMLField(blank=True)),
                ('submit_date', models.DateTimeField(auto_now=True, verbose_name='submitted')),
                ('answer_date', models.DateTimeField(editable=False, null=True, verbose_name='answered')),
                ('ability', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='skills.skill')),
                ('assigned_to', models.ForeignKey(limit_choices_to={'user__is_staff': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='players.player')),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='characters.character')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
            ],
        ),
    ]
