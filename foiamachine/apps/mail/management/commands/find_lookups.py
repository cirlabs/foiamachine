from apps.mail.models import thread_pattern, MailMessage
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    for mail_msg in MailMessage.objects.all():
        if mail_msg.body is not None:
            #any_matches = thread_pattern.findall(mail_msg.body)
            any_matches = [thread_pattern.findall(mail_msg.body), thread_pattern.findall(mail_msg.subject)]
            for any_match in any_matches:
                if len(any_match) > 0:
                    mail_msg.was_fwded = True
                    mail_msg.save()
        print 'DONE'
