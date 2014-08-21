from django.contrib import admin

from apps.mail.models import MailMessage, MailBox

class MailMessageAdmin(admin.ModelAdmin):
    list_display = ['email_from', 'dated', 'reply_to', 'subject', 'message_id']
    list_filter = ('reply_to', 'email_from', 'dated')
#admin.site.disable_action('delete_selected')
admin.site.register(MailMessage, MailMessageAdmin)
#admin.site.register(MailMessage)