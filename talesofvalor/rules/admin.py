"""Back end set up for Rules."""
from django.contrib import admin

from talesofvalor.rules.models import Rule

class RuleAdmin(admin.ModelAdmin):
    """Access the Comment from the admin."""
    pass

# Register the admin models
admin.site.register(Rule, RuleAdmin)