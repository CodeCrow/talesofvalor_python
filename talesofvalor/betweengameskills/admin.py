"""Back end set up for Between Game Skills."""
from django.contrib import admin

from talesofvalor.betweengameskills.models import BetweenGameSkill


class BetweenGameSkillAdmin(admin.ModelAdmin):
    """Access the BetweenGameSkill from the admin."""

    pass

# Register the admin models
admin.site.register(BetweenGameSkill, BetweenGameSkillAdmin)
