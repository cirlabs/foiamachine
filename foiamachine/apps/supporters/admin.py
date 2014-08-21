from django.contrib import admin

from .models import SupportLevel, Supporter


class SupportLevelAdmin(admin.ModelAdmin):
    pass


class SupporterAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'support_level']
    list_filter = ('support_level',)

admin.site.register(SupportLevel, SupportLevelAdmin)
admin.site.register(Supporter, SupporterAdmin)
