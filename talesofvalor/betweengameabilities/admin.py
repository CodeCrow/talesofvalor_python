"""Back end set up for Between Game Skills."""
from django.contrib import admin

from talesofvalor.betweengameabilities.models import BetweenGameAbility


class BetweenGameAbilityAdmin(admin.ModelAdmin):
    """Access the BetweenGameAbility from the admin."""
    verbose_name = "Between Game Ability"
    verbose_name_plural = "Between Game Abilities"


# Register the admin models
admin.site.register(BetweenGameAbility, BetweenGameAbilityAdmin)
