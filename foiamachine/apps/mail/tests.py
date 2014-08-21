import apps
from django.test import TestCase
from django.contrib.auth.models import User


class EMailTest(TestCase):

    def test_email(self):
        # Create conventional Django user
        user = User.objects.create_user(
            'john',
            'lennon@thebeatles.com',
        )

        # Create FOIA Machine org 
        org = apps.users.models.Organization(name="test")
        org.save()

        # Create FOIA Machine user profile linked to user and org
        usr = apps.users.models.UserProfile(user=user)
        user.userprofile.organizations.add(org)
        user.save()

        # Create mailbox for FOIA Machine user
        mailbox = apps.mail.models.MailBox(usr=user)
        mailbox.save()

        # Create message
        message = apps.mail.models.MailMessage.objects.create(
            email_from=mailbox.get_provisioned_email(),
            subject='test mail',
            body='lkjadflkjsf'
        )

        email1 = apps.core.models.EmailAddress.objects.create(
            content='shifflett.shane@gmail.com'
        )
        message.to.add(email1)

        email2 = apps.core.models.EmailAddress.objects.create(
            content=usr.get_email()
        )
        message.cc.add(email2)

        message.save()

        # Send message
        message.send(email1)
        mailbox.add_message(message)

        # Finish
        self.assertEqual(1 + 1, 2)
