"""Back end set up for Player."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from talesofvalor.players.models import Player, Registration,\
    RegistrationRequest, PEL


# Define an inline admin descriptor for Player model
# which acts a bit like a singleton
class PlayerInline(admin.StackedInline):
    """So players can be added for users."""

    model = Player
    can_delete = False
    verbose_name_plural = 'players'


# Define a new User admin
class PlayerAdmin(BaseUserAdmin):
    """Define the admin for new users."""

    inlines = (PlayerInline, )


# sure we can see the modified and created dates
class PELAdmin(admin.ModelAdmin):
    
    readonly_fields = ['created', 'modified']


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, PlayerAdmin)
admin.site.register(Registration)
admin.site.register(RegistrationRequest)
admin.site.register(PEL, PELAdmin)
