"""Back end set up for Rules."""
from django.contrib import admin

from talesofvalor.rules.models import Rule, Prerequisite,\
    PrerequisiteGroup


class RuleAdmin(admin.ModelAdmin):
    """Access the Rule from the admin."""
    pass


class PrerequisiteAdmin(admin.ModelAdmin):
    """Access the Prereq from the admin."""
    pass


class PrerequisiteGroupAdmin(admin.ModelAdmin):
    """Access the Prereq Grlupfrom the admin."""
    pass


# Register the admin models
admin.site.register(Rule, RuleAdmin)
admin.site.register(Prerequisite, PrerequisiteAdmin)
admin.site.register(PrerequisiteGroup, PrerequisiteGroupAdmin)
