from django.db.models import Count
from django.core.validators import validate_email

from apps.agency.models import Agency
from apps.core.models import EmailAddress
from apps.contacts.models import Contact, Phone, Address, Note, Title, EmailAddress
#from apps.agency.api import AgencyResource


from tastypie import http
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie.exceptions import BadRequest, TastypieError, ApiFieldError
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS, patch_cache_control
from tastypie.validation import Validation

from django.db import transaction

from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt

from tastypie.cache import SimpleCache

import simplejson as json


import logging
logger = logging.getLogger('default')


class ContactAuthentication(Authentication):
    def is_authenticated (self, request):
        return request.user.is_authenticated()
    
class ContactValidation(Validation):
    def is_valid(self, bundle, request=None):
        one_contact_method = False
        for field in ['addresses', 'emails']:
            for val in bundle.data[field]:
                if val.strip() != '':
                    one_contact_method = True
        if not one_contact_method:
            return "Please enter at least one method of contact (mailing address or email)."
        if not bundle.data:
            return 'No data submitted'
        for email in bundle.data['emails']:
            #we guarantee at least one contact method is present, if an doesn't exist that doesn't disqualify a contact
            if email.strip() != '':
                try:
                    validate_email(email)
                except ValidationError:
                    return "Please enter a valid email address."
                if EmailAddress.objects.filter(content=email):
                    emailobj = EmailAddress.objects.get(content=email)
                    retstr = 'Already have a contact with that email address'
                    contacts = Contact.objects.filter(emails__content=emailobj)
                    if contacts:
                        retstr += ' in agency ' + contacts[0].agency_related_contacts.all()[0].name
                        retstr += ". Please use a unique address."
                        if 'id' in bundle.data and str(contacts[0].id) != bundle.data['id']:
                            return retstr
        return {}


def contact_is_valid(bundle, request=None):
    one_contact_method = False
    for field in ['addresses', 'emails']:
        if field in bundle.data.keys():
            one_contact_method = True
    if not one_contact_method:
        return "Please enter at least one method of contact (mailing address or email)."
    if not bundle.data:
        return 'No data submitted'
    if 'emails' in bundle.data.keys():
        for email in bundle.data['emails']:
            #import pdb;pdb.set_trace()
            #we guarantee at least one contact method is present, if an doesn't exist that doesn't disqualify a contact
            if email.strip() != '':
                try:
                    validate_email(email)
                except ValidationError:
                    return "Please enter a valid email address."
                #if EmailAddress.objects.filter(content=email).count() > 0:
                    #emailobj = EmailAddress.objects.get(content=email)
                    #retstr = 'Already have a contact with that email address'
                    #contacts = Contact.objects.filter(emails__content=emailobj)
                    #if contacts:
                        #retstr += ' in agency ' + contacts[0].agency_related_contacts.all()[0].name
                        #retstr += ". Please use a unique address."
                        #return retstr
                        #if 'id' in bundle.data and str(contacts[0].id) != bundle.data['id']:
                        #    return retstr
    return ''



class ContactResource(ModelResource):
    agencies = fields.ToManyField('apps.agency.api.AgencyResource', 'agency_related_contacts')
    
    class Meta:
        queryset = Contact.objects.all_them()
        resource_name = 'contact'
        allowed_methods = ['get', 'post', 'put']
        detail_allowed_methods = ['get', 'post', 'put']
        #authorization = Authorization()
        #authentication = ContactAuthentication()
        always_return_data = True
        filtering = {
            'id': ALL,
            'slug': ALL,
            'agencies': ALL_WITH_RELATIONS
        }
        validation = ContactValidation()
        #cache = SimpleCache()

    def dehydrate(self, bundle):
        bundle.data['emails'] = [e.content for e in bundle.obj.emails.all()]
        bundle.data['titles'] = [e.content for e in bundle.obj.titles.all()]
        notes = map(lambda x: x.get_content, bundle.obj.notes.all())
        bundle.data['notes'] = ' '.join(notes)
        bundle.data['phone'] = [e.content for e in bundle.obj.phone_numbers.all()]
        bundle.data['addresses'] = [e.content for e in bundle.obj.addresses.all()]
        bundle.data['can_edit'] = (bundle.request.user.is_superuser or bundle.request.user.is_staff or bundle.request.user == bundle.obj.creator)
        agencies = bundle.obj.get_related_agencies()
        agencynames = map(lambda x: x.name, agencies)
        bundle.data['statute_slugs'] = []
        for agency in agencies:
            for statute in agency.government.statutes.all():
                bundle.data['statute_slugs'].append(statute.slug)
        bundle.data['agency_names'] = ','.join(agencynames)
        return bundle


    def obj_update(self, bundle, **kwargs):
        data = bundle.data
        user = bundle.request.user
        contact = bundle.obj = Contact.objects.all_them().get(id=data['id'])
        if not (bundle.request.user.is_superuser or bundle.request.user.is_staff or bundle.request.user == bundle.obj.creator):
            raise BadRequest("It appears you cannot edit this contact")
        if len(contact_is_valid(bundle)) > 0:
            raise BadRequest(contact_is_valid(bundle))

        MAX_EMAIL_ADDRESSES = 1

        for field in ['first_name', 'last_name', 'middle_name', 'dob']:
            if field in data:
                setattr(contact, field, data[field])

        if 'hidden' in data:
            hidden = data['hidden']
            contact.hidden = hidden
            if hidden:
                #deactive all the emails
                map(lambda email: email.deactive(), contact.emails.all())
            else:
                for email in contact.emails.all():
                    if EmailAddress.objects.filter(content=email).count() > 1:
                        #there is more than one email
                        raise BadRequest("Another contact has been created with this email. To un-delete this contact please change its email address or remove it.")
                    else:
                        email.deprecated = None
                        email.save()

        if 'emails' in data:
            if type (data['emails']) == list:
                # Just a list of email addresses
                try:
                    for i in range(min(MAX_EMAIL_ADDRESSES, len(data['emails']))):
                        if data['emails'][i].strip() != '':
                            try:
                                email = contact.emails.all()[i]
                                email.content = data['emails'][i]
                                email.save()
                            except:
                                #the email is new and not edited
                                eaddr = EmailAddress(content = data['emails'][i])
                                eaddr.save()
                                contact.emails.add(eaddr)
                except Exception as e:
                    logger.exception("Failure to update email %s" % e)
            elif type (data['emails']) == dict:
                # By ID
                # Should be of the form { '123' : 'jsmith@example.com' }
                try:
                    contactEmails = contact.emails.all()
                    for pk, address in data['emails'].iteritems():
                        email = EmailAddress.objects.get(id = int(pk))
                        assert (email in contactEmails)
                        email.content = address
                        email.save()
                except Exception as e:
                    logger.exception("Failure to update email %s" % e)

        if 'notes' in data:
            notes = [Note(content = x) for x in data['notes'] if x]
            for note in notes:
                note.save()
            contact.notes = notes
        if 'phone' in data:
            phone_numbers = [Phone(content = x) for x in data['phone'] if x]
            for number in phone_numbers:
                number.save()
            contact.phone_numbers = phone_numbers
        if 'titles' in data:
            titles = [Title(content = x) for x in data['titles'] if x]
            for title in titles:
                title.save()
            contact.titles = titles
        if 'addresses' in data:
            addresses = [Address(content = x) for x in data['addresses'] if x]
            for address in addresses:
                address.save()
            contact.addresses = addresses
        contact.save()
        return bundle

    def obj_create(self, bundle, **kwargs):
        try:
            data = bundle.data
            user = bundle.request.user
            if user.is_anonymous:
                user = None
            if len(contact_is_valid(bundle)) > 0:
                raise BadRequest(contact_is_valid(bundle))
            data['dob'] = data['dob'] or None if 'dob' in data.keys() else None # Empty string no good
            agencyId = data['agencyId']
            del data['agencyId']
            emails = [EmailAddress.get_or_create(email)[0] for email in data['emails'] if email]
            map(lambda x: x.save(), emails)
            notes = [Note(content = data['notes'], user = user)]
            del data['notes']
            map(lambda x: x.save(), notes)
            titles = [Title(content = title) for title in data['titles'] if title]
            del data['titles']
            map(lambda x: x.save(), titles)
            del data['emails']
            phone_numbers = [Phone(content = phone) for phone in data['phone_numbers'] if phone]
            del data['phone_numbers']
            map(lambda x: x.save(), phone_numbers)
            addresses = [Address(content = address) for address in data['addresses'] if address]
            map(lambda x: x.save(), addresses)
            del data['addresses']
            print agencyId
            agency = Agency.objects.get(id=agencyId)
            thecontact = Contact(**data)
            thecontact.save()
            thecontact.titles = titles
            thecontact.emails = emails
            thecontact.phone_numbers = phone_numbers
            thecontact.addresses = addresses
            thecontact.notes = notes
            thecontact.agency_related_contacts = [agency]
            thecontact.creator = user
            thecontact.save()
            agency.save()
            bundle.obj = thecontact
            return bundle
        except Exception as e:
            logger.exception(e)
            raise BadRequest (str(e))
