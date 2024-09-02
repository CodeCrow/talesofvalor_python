"""Back end set up for Between Game Skills."""
from django.contrib import admin

from talesofvalor.attendance.models import Attendance


class AttendanceAdmin(admin.ModelAdmin):
    """Access the Attendance from the admin."""
    list_display = ('event', 'player', 'character', )

# Register the admin models
admin.site.register(Attendance, AttendanceAdmin)
