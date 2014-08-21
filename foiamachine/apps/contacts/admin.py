from django.contrib import admin

from apps.contacts.models import Contact, Title, Phone, Address, Note

class ContactAdmin(admin.ModelAdmin):
    search_fields = ['emails__content', 'first_name', 'last_name']

admin.site.register(Contact, ContactAdmin)
admin.site.register(Title, admin.ModelAdmin)
admin.site.register(Phone, admin.ModelAdmin)
admin.site.register(Address, admin.ModelAdmin)
admin.site.register(Note, admin.ModelAdmin)
