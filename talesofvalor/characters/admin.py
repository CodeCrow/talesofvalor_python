"""Back end set up for characters."""
from django.contrib import admin

from talesofvalor.characters.models import Character, CharacterGrant,\
    CharacterEventInfluence, CorruptionLevel


class CharacterAdmin(admin.ModelAdmin):
    """Access the Character from the admin."""
    readonly_fields = ('cp_initial',)
    search_fields = ('name',)


class CorruptionLevelAdmin(admin.ModelAdmin):
    """
    Maintain the corruption ladder.

    This is how staff retune the thresholds without a code change.
    """
    list_display = ('name', 'threshold')
    list_editable = ('threshold',)
    ordering = ('-threshold',)


class CharacterEventInfluenceAdmin(admin.ModelAdmin):
    """
    Per event influence rows.

    The computed values are read only here; they are set by processing the
    event, which keeps the character's current influence in step.
    """
    list_display = (
        'character',
        'event',
        'influence_input',
        'start_influence',
        'end_influence',
        'corruption_flag',
        'corruption_level',
        'processed_at',
    )
    list_filter = ('event', 'corruption_flag', 'corruption_level')
    search_fields = ('character__name',)
    raw_id_fields = ('character',)
    readonly_fields = (
        'start_influence',
        'end_influence',
        'corruption_flag',
        'corruption_level',
        'processed_at',
        'processed_by',
    )


# Register the admin models
admin.site.register(Character, CharacterAdmin)
admin.site.register(CharacterGrant)
admin.site.register(CorruptionLevel, CorruptionLevelAdmin)
admin.site.register(CharacterEventInfluence, CharacterEventInfluenceAdmin)
