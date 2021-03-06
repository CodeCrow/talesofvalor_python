# Generated by Django 2.1.9 on 2019-09-15 13:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('origins', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='origin',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='origin',
            name='created_by',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='origins_origin_author', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='origin',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='last updated'),
        ),
        migrations.AlterField(
            model_name='origin',
            name='modified_by',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='origins_origin_updater', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='origin',
            name='type',
            field=models.CharField(choices=[('race', 'Race'), ('background', 'Background')], default='race', max_length=15, verbose_name='Type'),
        ),
    ]
