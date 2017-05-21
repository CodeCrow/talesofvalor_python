"""Back end set up for Events."""
from django.contrib import admin

from talesofvalor.events.models import Event

class EventAdmin(admin.ModelAdmin):
    """Access the Event from the admin."""
    pass

# Register the admin models
admin.site.register(Event, EventAdmin)