from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from django.db import migrations


GROUP_NAMES = ("Staff", "Admin")


def _influence_permission():
    """
    Get the update_influence permission, creating it if it isn't there yet.

    Permissions are normally created by a post_migrate signal, which hasn't
    run while migrations are still being applied.  On a database built from
    scratch this migration would otherwise be looking for a row that doesn't
    exist yet.
    """
    content_type, _ = ContentType.objects.get_or_create(
        app_label='characters',
        model='character'
    )
    permission, _ = Permission.objects.get_or_create(
        codename='update_influence',
        content_type=content_type,
        defaults={'name': 'Can update influence'}
    )
    return permission


def add_permission_to_group(apps, schema_editor):
    permission = _influence_permission()
    for group_name in GROUP_NAMES:
        group, _ = Group.objects.get_or_create(name=group_name)
        group.permissions.add(permission)


def remove_permission_from_group(apps, schema_editor):
    try:
        permission = Permission.objects.get(codename='update_influence')
    except Permission.DoesNotExist:
        return
    for group_name in GROUP_NAMES:
        group, _ = Group.objects.get_or_create(name=group_name)
        group.permissions.remove(permission)


class Migration(migrations.Migration):

    dependencies = [
        ('characters', '0031_character_influence'),
    ]

    operations = [
        migrations.RunPython(add_permission_to_group, remove_permission_from_group),
    ]
