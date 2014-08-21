from django.contrib import admin

from apps.core.models import EmailAddress

class EmailAdmin(admin.ModelAdmin):
    search_fields = ['content']

admin.site.register(EmailAddress, EmailAdmin)
