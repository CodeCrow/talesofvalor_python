"""Back end set up for Origin."""
from django.contrib import admin

from talesofvalor.origins.models import Origin


class OriginAdmin(admin.ModelAdmin):
    """Access the Event from the admin."""
    pass

# Register the admin models
admin.site.register(Origin, OriginAdmin)
