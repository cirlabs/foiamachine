from django.contrib import admin

from .models import Agency

class AgencyAdmin(admin.ModelAdmin):
    search_fields = ['name', 'government__name', 'contacts__emails__content', 'contacts__last_name']
    
admin.site.register(Agency, AgencyAdmin)
