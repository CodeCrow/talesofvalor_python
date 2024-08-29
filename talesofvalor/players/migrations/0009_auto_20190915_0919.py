# Generated by Django 2.1.9 on 2019-09-15 13:19

from django.db import migrations, models
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0008_player_staff_attention_flag'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AlterField(
            model_name='pel',
            name='best_moments',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='pel',
            name='data',
            field=djangocms_text_ckeditor.fields.HTMLField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='pel',
            name='dislikes',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='pel',
            name='learned',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='pel',
            name='likes',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='pel',
            name='rating',
            field=models.PositiveIntegerField(choices=[(5, 'Amazing'), (4, 'Good'), (3, 'Average'), (2, 'Fair'), (1, 'Poor')]),
        ),
        migrations.AlterField(
            model_name='pel',
            name='worst_moments',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='registration',
            name='cabin',
            field=models.CharField(blank=True, default='', help_text='What cabin is the player staying in?', max_length=100),
        ),
        migrations.AlterField(
            model_name='registration',
            name='notes',
            field=models.TextField(blank=True, default=''),
        ),
    ]
