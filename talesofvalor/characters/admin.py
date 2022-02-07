"""Back end set up for characters."""
from django.contrib import admin

from talesofvalor.characters.models import Character, CharacterGrant


class CharacterAdmin(admin.ModelAdmin):
    """Access the Character from the admin."""
    pass


# Register the admin models
admin.site.register(Character, CharacterAdmin)
admin.site.register(CharacterGrant)
