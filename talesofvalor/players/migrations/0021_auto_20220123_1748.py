# Generated by Django 3.2.11 on 2022-01-23 22:48

from django.db import migrations, models
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0020_merge_20220109_1558'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pel',
            name='code',
        ),
        migrations.RemoveField(
            model_name='pel',
            name='data',
        ),
        migrations.AddField(
            model_name='pel',
            name='devout',
            field=models.TextField(blank=True, default='', verbose_name='If you are Devout or Supplicant to a faith, please tell us how you practiced and demonstrated your beliefs.'),
        ),
        migrations.AddField(
            model_name='pel',
            name='new_rule_dislikes',
            field=models.TextField(blank=True, default='', verbose_name="Is there anything you didn't care for about the new rules and systems and what do you think would improve it?"),
        ),
        migrations.AddField(
            model_name='pel',
            name='new_rule_likes',
            field=models.TextField(blank=True, default='', verbose_name="Is there anything you really liked about the new rules and systems we've implemented?"),
        ),
        migrations.AddField(
            model_name='pel',
            name='plans',
            field=models.TextField(blank=True, default='', verbose_name="What are you character's current interests and plans? What do you think you'll be working on moving forward?"),
        ),
        migrations.AddField(
            model_name='pel',
            name='what_did_you_do',
            field=djangocms_text_ckeditor.fields.HTMLField(blank=True, default='', verbose_name='What did you do during this event?'),
        ),
        migrations.AlterField(
            model_name='pel',
            name='favorites',
            field=models.TextField(blank=True, default='', verbose_name='What did you enjoy?'),
        ),
        migrations.AlterField(
            model_name='pel',
            name='heavy_armor_worn_flag',
            field=models.BooleanField(default=False, help_text='This character wore heavy armor the entire event.', verbose_name='Character wore heavy armor this event (cheaper Health pre-req)?'),
        ),
        migrations.AlterField(
            model_name='pel',
            name='learned',
            field=models.TextField(blank=True, default='', verbose_name='Did your character learn new skills or spells during game?  If so, list them here.'),
        ),
        migrations.AlterField(
            model_name='pel',
            name='suggestions',
            field=models.TextField(blank=True, default='', verbose_name='What do you think could be improved?'),
        ),
    ]
