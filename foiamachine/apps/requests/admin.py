from django.contrib import admin

from .models import Event, Request, RecordType, ResponseFormat


########## INLINES ##########
class EventInline(admin.TabularInline):
    model = Event


########## ADMINS ##########
def make_deleted(modeladmin, request, queryset):
    queryset.update(status='X')
make_deleted.short_description = "Mark selected requests as 'deleted'"


class RequestAdmin(admin.ModelAdmin):
    inlines = [EventInline]
    list_display = ['title', 'date_added', 'status', 'author']
    list_filter = ('author__username', 'status', 'agency__name', 'government__name')
    actions = [make_deleted]

admin.site.disable_action('delete_selected')
admin.site.register(Request, RequestAdmin)
admin.site.register(Event, admin.ModelAdmin)
admin.site.register(ResponseFormat, admin.ModelAdmin)
admin.site.register(RecordType, admin.ModelAdmin)
