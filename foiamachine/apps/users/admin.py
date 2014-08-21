from django.contrib import admin
from apps.users.models import UserProfile, Organization, PermissionGroup, InterestedParty

class InterestedPartyAdmin(admin.ModelAdmin):
    list_filter = ('first_name', 'last_name', 'email')
admin.site.register(InterestedParty, InterestedPartyAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserProfile, UserProfileAdmin)


class OrganizationAdmin(admin.ModelAdmin):
    pass
admin.site.register(Organization, OrganizationAdmin)

class PermissionGroupAdmin(admin.ModelAdmin):
    pass
admin.site.register(PermissionGroup, PermissionGroupAdmin)
