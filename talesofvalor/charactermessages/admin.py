"""Back end set up for Events."""
from django.contrib import admin

from talesofvalor.charactermessages.models import CharacterMessage

# Register the admin models
admin.site.register(CharacterMessage)