from django.contrib import admin
'''
from .models import *

class ExemptionInline(admin.StackedInline):
    model = Exemption
    extra = 0
    
class FeeWaiverInline(admin.StackedInline):
    model = FeeWaiver
    extra = 0
    
class StatuteAdmin(admin.ModelAdmin):
    inlines = [FeeWaiverInline, ExemptionInline]

admin.site.register(Language, admin.ModelAdmin)
admin.site.register(AdminName, admin.ModelAdmin)
admin.site.register(Nation, admin.ModelAdmin)
admin.site.register(Government, admin.ModelAdmin)
admin.site.register(ExemptionType, admin.ModelAdmin)
admin.site.register(Statute, StatuteAdmin)
'''