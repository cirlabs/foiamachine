from django.forms.widgets import RadioSelect, DateInput
from django.forms.extras.widgets import SelectDateWidget
from django.forms import ModelForm
from django.db.models import Count
from django.conf import settings
from django.db.models import Q
from django import forms
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group

from .models import Request, RecordType, ResponseFormat, request_statuses 
from apps.government.models import Government
from apps.agency.models import Agency
from apps.mail.views import SizeLimitedFileField

from taggit.models import Tag


def init_pubprivate(request):
    return {'private': 't' if request.private else 'f',
            'title': request.title,
            'related_request_field': request.pk
            }


def init_gov(request):
    lvl = -1 if request.government is None else request.government.level

    def get_field(level):
        return request.government.pk if lvl == level else None
    return {
        'national_field': request.government.nation.pk if request.government is not None and request.government.nation is not None else None,
        'state_field': get_field(1),
        'local_field': get_field(2) or get_field(3),
        'related_request_field': request.pk
    }


def init_topic_agency(request):
    return {
        'topic_field': 1,
        'agency_field': request.agency.pk if request.agency is not None else None,
        'contacts_hidden_field': request.contacts.all()[0].id if len(request.contacts.all()) > 0 else None,
        'related_request_field': request.pk
    }


def init_datesfrom(request):
    return {
        'request_start_date': request.request_start_date if request.request_start_date is not None else None,
        'request_end_date': request.request_end_date if request.request_end_date is not None else None,
        'related_request_field': request.pk
    }


def init_requestbody(request):
    return {
        'record_types': [rc.pk for rc in request.record_types.all()],
        'body_text': request.text,
        'related_request_field': request.pk
    }


def init_finalsteps(request):
    print request.fee_waiver
    return {
        'fee_waiver_field': 1 if request.fee_waiver is True else 0,
        'fee_level_field': request.max_cost if request.max_cost else 0,
        'response_formats_field': [rf.pk for rf in request.acceptable_responses.all()],
        'related_request_field': request.pk
    }


def init_preview(request):
    return {
        'to_send': 1,
        'related_request_field': request.pk
    }


class PubPrivateForm(forms.Form):
    title = forms.CharField(required=False)
    private = forms.BooleanField(label='Who can see this request?', widget=forms.RadioSelect(choices=(('f', 'Public request'), ('t', 'Keep this request private'),)), initial='t')
    related_request_field = forms.IntegerField(widget=forms.HiddenInput())


class GovernmentForm(forms.Form):

    inter_super_national_field = forms.ModelChoiceField(queryset=\
        Government.objects.filter(level__in=['I','S']), label='International\
         and super-national governments', required=False,\
          widget=forms.Select(attrs={'class': 'gov international span4'}))

    national_field = forms.ModelChoiceField(queryset=Government.objects.filter(level__in=['0']),\
     label='Nations/National governments',\
      required=False, widget=forms.Select(attrs={'class':'gov national span4'}))

    state_field = forms.ModelChoiceField(queryset=Government.objects.filter(level__in=['1']),\
     label='State governments', required=False, widget=forms.Select(attrs={'class':'gov state span4'}))

    local_field = forms.ModelChoiceField(queryset=Government.objects.filter(level__in=['2','3']),\
     label='Local governments', required=False, widget=forms.Select(attrs={'class':'gov local span4'}))

    gov_selection_field = forms.IntegerField(label='Government choice',\
     widget=forms.HiddenInput(attrs={'class':'gov-selection'}))

    related_request_field = forms.IntegerField(widget=forms.HiddenInput())


class TopicAgencyForm(forms.Form):
    #topic_field = forms.ModelChoiceField(label='Choose a topic for your request',\
    #    widget=forms.Select, queryset=Tag.objects.all(), required=False)
    #Agency.objects.all().annotate(Count('contacts')).filter(contacts__count__gt=0).order_by('-created')
    agency_field = forms.ModelChoiceField(queryset=Agency.objects.all().annotate(Count('contacts')).filter(contacts__count__gt=0).order_by('-created'),\
        label='Choose the agency for your request', required=False)

    contacts_hidden_field = forms.CharField(label='Contact choices',\
     widget=forms.HiddenInput(attrs={'class':'contacts-selections span12'}))

    related_request_field = forms.IntegerField(widget=forms.HiddenInput())


class DatesForm(forms.Form):
    request_start_date = forms.DateField(label='Start date', widget=DateInput, required=False)
    request_end_date = forms.DateField(label='End date', widget=DateInput, required=False)
    related_request_field = forms.IntegerField(widget=forms.HiddenInput())


class RequestBody(forms.Form):
    record_types = forms.ModelMultipleChoiceField(queryset=RecordType.objects.all(), label='What types of records do you want?', required=False)

    pertaining_to = forms.CharField(widget=forms.TextInput, required=False)

    body_text = forms.CharField(label='Or, explain in your own words what you want', widget=forms.Textarea(attrs={'cols':'', 'rows': ''}), required=False)

    related_request_field = forms.IntegerField(widget=forms.HiddenInput())


class FinalStepsForm(forms.Form):
    BOOL_CHOICES = (('1', 'Yes'), ('0', 'No'),)
    FEE_LEVELS = ((0, 'There will be any cost',),\
        (25, 'The cost will exceed $25',), (50, 'The cost will exceed $50',),\
         (100, 'The cost will exceed $100',),)
    
    fee_waiver_field = forms.ChoiceField(label='Do you want to request that search and duplication fees be waived or reduced?',\
     widget=forms.RadioSelect, choices=BOOL_CHOICES, initial='1', required=False)
    
    fee_level_field = forms.ChoiceField(label='Ask the agency to contact you to justify the cost of fulfilling your request if ...',\
     widget=forms.RadioSelect, choices=FEE_LEVELS, initial=0)
    
    specify_formats_field = forms.ChoiceField(label='Do you want to specify the formats in which you would like to receive a response?',\
     widget=forms.RadioSelect, choices=BOOL_CHOICES, initial='0', required=False)

    prefer_electronic_field = forms.ChoiceField(label='Do you want to request the agency fulfill your request electronically?',\
     widget=forms.RadioSelect, choices=BOOL_CHOICES, initial='1', required=False) 

    prefer_phone_field = forms.ChoiceField(label='Do you want to request the agency contact you via telephone rather than by mail?',\
     widget=forms.RadioSelect, choices=BOOL_CHOICES, initial='1', required=False) 

    response_formats_field = forms.ModelMultipleChoiceField(queryset=ResponseFormat.objects.all(),\
     label='What specific formats are acceptable?', required=False)

    related_request_field = forms.IntegerField(widget=forms.HiddenInput())


class PreviewForm(forms.Form):
    SEND_CHOICES = (
        (1, "Now"),
        (2, "Later"),
    )
    #to_send = forms.ChoiceField(widget=forms.RadioSelect, choices=SEND_CHOICES)
    #scheduled_date = forms.DateField(required=False)
    related_request_field = forms.IntegerField(widget=forms.HiddenInput())
    body_text = forms.CharField(label='', widget=forms.Textarea(attrs={'cols':'', 'rows': ''}), required=False)
    file = SizeLimitedFileField(required=False)



class FilterForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['tags'].queryset = user.tags
        self.fields['agency'].queryset = Agency.objects.filter(id__in=Request.objects.filter(author=user.user, agency__isnull=False).values_list("agency"), hidden=False, deprecated__isnull=True).order_by('name')

    filtering = forms.IntegerField (required = True)

    agency = forms.ModelChoiceField(queryset = Agency.objects.filter(hidden=False, deprecated__isnull=True).order_by('name'), required=False, empty_label="Any Agency")
    status = forms.ChoiceField(choices = (('A', 'All requests'),) + request_statuses, initial='A', required = False, label = "Any status")

    added_before = forms.DateField(required=False)
    added_after = forms.DateField(required=False)

    response_required_before = forms.DateField(required=False)
    response_required_after = forms.DateField(required=False)
    tags = forms.ModelMultipleChoiceField(queryset = Tag.objects, required = False)


class UpdateForm(forms.Form):
    action = forms.ChoiceField(choices=(
        ('Make Public', 'Make Public'),
        ('Make Private', 'Make Private'),
        ('Delete', 'Delete'),
        ('Update', 'Update')

    ), required=False)

    requests_to_modify = forms.ModelMultipleChoiceField(queryset=Request.objects.all(), required=False)

    newstatus = forms.ChoiceField(request_statuses, required = False)
    newsubject = forms.CharField(required = False)
    newduedate = forms.DateTimeField(required = False)
    newupdateddate = forms.DateTimeField(required = False)
    newfulfilleddate = forms.DateTimeField(required = False)
    addgroups = forms.ModelMultipleChoiceField(queryset = Group.objects.all(), required = False)
    removegroups = forms.ModelMultipleChoiceField(queryset = Group.objects.all(), required = False)


#begin forms from original birddog
class RequestForm(forms.ModelForm):
    class Meta:
        model = Request


class NewRequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ('title', 'private')
        widgets = {
            'private': forms.widgets.CheckboxInput
        }


class NewOptionalRequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ('text', 'tags', 'documents')
