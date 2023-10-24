"""Back end set up for Between Game Skills."""
from django.contrib import admin

from talesofvalor.betweengameabilities.models import BetweenGameAbility


class BetweenGameAbilityAdmin(admin.ModelAdmin):
    """Access the BetweenGameAbility from the admin."""

    pass


# Register the admin models
admin.site.register(BetweenGameAbility, BetweenGameAbilityAdmin)
