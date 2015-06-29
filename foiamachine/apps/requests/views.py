from django.db.models import Count, Avg
from django.contrib.formtools.wizard.views import SessionWizardView
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User, Group
from django.template import RequestContext
import django.template
from django.forms import ModelChoiceField
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.core.files.storage import DefaultStorage
from guardian.shortcuts import get_perms, assign_perm, remove_perm, get_groups_with_perms

from apps.mail.views import setup_message_reassignment
from apps.mail.models import MailBox, Attachment
from apps.government.models import Government
from apps.requests.models import Agency, Request, ViewableLink
from apps.contacts.models import Contact
from apps.requests.forms import PubPrivateForm,\
    GovernmentForm, TopicAgencyForm, DatesForm,UpdateForm,\
    RequestBody, FinalStepsForm, PreviewForm, FilterForm,\
    init_pubprivate, init_gov, init_topic_agency,\
    init_datesfrom, init_requestbody, init_finalsteps, init_preview

from apps.users.forms import InterestedPartyForm
from apps.users.models import UserProfile, InterestedParty, get_non_user_groups

from guardian.shortcuts import get_objects_for_group

from datetime import datetime, timedelta
from itertools import chain
import pytz
import re
import logging

logger = logging.getLogger('default')
register = django.template.Library()


PUBLIC_FORMS = [
    ("pub-private", PubPrivateForm),
    ("gov", GovernmentForm),
    ("agency", TopicAgencyForm),
    ("dates", DatesForm),
    ("body", RequestBody),
    ("misc", FinalStepsForm),
    ("preview", PreviewForm),
]

TEMPLATES = {
    "pub-private": "requests/forms/pub_private_form.html",
    "gov": "requests/forms/gov_form.html",
    "agency": "requests/forms/agency_form.html",
    "dates": "requests/forms/dates_form.html",
    "body": "requests/forms/body_form.html",
    "misc": "requests/forms/misc_form.html",
    "preview": "requests/forms/interview_preview.html",
}

STEP_DISPLAY = {
    "pub-private": "Start",
    "gov": "Government",
    "gov-public": "Government",
    "agency": "Topic/Agency",
    "dates": "Dates",
    "body": "Types of records",
    "misc": "Final details",
    "preview": "Preview/Send",
}

def get_groups_and_usergroups(user):
    '''
    Return a list of groups a user can share a request with
    Each user has their own group that is the same as their username
    We want a request to be shared with any other user
    Or shared with any groups the user creates
    '''
    #TODO make the groups for users a model so we can query this OR find a better union test
    groups = Group.objects.all()
    users = User.objects.all()
    results = list()
    for group in groups:
        for usr in users:
            if usr.username == group.name and usr.username != 'AnonymousUser':
                results.append(group)
    return list(chain(user.groups.all(), results))

def show_pubprivate_form(wizard):
    try:
        up = UserProfile.objects.get(user=wizard.request.user)
        return up.is_pro
    except Exception as e:
        logger.exception(e)
    #public by default!
    return False

def overall_stats(request):
    context = {}
    requests = Request.objects.filter(status__in=['P','F','D','R','S']).exclude(agency__name='THE TEST AGENCY')
    if 'start_date' in request.GET:
        try:
            start_date = request.GET['start_date']
            dt = datetime.strptime(start_date, "%Y-%m-%d")
            requests = requests.exclude(date_updated__lt=dt)
        except ValueError:
            # Couldn't parse date
            pass
    if 'end_date' in request.GET:
        try:
            end_date = request.GET['end_date']
            dt = datetime.strptime(end_date, "%Y-%m-%d")
            requests = requests.exclude(date_updated__gt=dt)
        except:
            # Couldn't parse date
            pass

    context['num_sent'] = requests.filter(scheduled_send_date__lte=datetime.now()).count()
    context['sent_to_feds'] = requests.filter(scheduled_send_date__lte=datetime.now(), government__name='United States of America').count()
    context['total_agencies'] = Agency.objects.all().count()
    context['num_agencies'] = len(set(requests.filter(agency__isnull=False, scheduled_send_date__lte=datetime.now()).values_list("agency", flat=True)))
    context['num_governments'] = len(set(requests.filter(government__isnull=False, scheduled_send_date__lte=datetime.now()).values_list("government", flat=True)))
    context['num_requests_filed'] = requests.exclude(status='X').exclude(status='I').exclude(status='U').count()
    context['num_partially_fulfilled'] = requests.filter(status='P').count()
    context['num_fulfilled'] = requests.filter(status='F').count()
    context['num_denied'] = requests.filter(status='D').count()
    context['num_other_responses'] = requests.filter(status='R').count()
    context['num_no_response'] = requests.filter(status='S').count()
    context['avg_first_response_time'] = requests.filter(first_response_time__gt=0).aggregate(Avg('first_response_time'))['first_response_time__avg']
    context['avg_lifetime'] = requests.filter(lifetime__gt=0).aggregate(Avg('lifetime'))['lifetime__avg']
    context['avg_days_outstanding'] = requests.filter(days_outstanding__gt=0).aggregate(Avg('days_outstanding'))['days_outstanding__avg']
    context['id'] = 1

    if context['avg_first_response_time'] is None:
        context['avg_first_response_time'] = -1
    if context['avg_lifetime'] is None:
        context['avg_lifetime'] = -1
    if context['avg_days_outstanding'] is None:
        context['avg_days_outstanding'] = -1
    
    return render_to_response('requests/overall_stats.json', context, context_instance=RequestContext(request))

def disallow_sunset(request, pk=None, template='requests/request_detail.html'):
    context = {}
    if pk is not None:
        req = get_object_or_404(Request, pk=pk)
        req.keep_private = True
        req.save()
        return HttpResponseRedirect("/%s/%s/" % ('requests', pk))
    return render_to_response('403.html', {}, context_instance=RequestContext(request))

def send_limit(request, pk=None, template='requests/send_limit.html'):
    context = {}
    user = request.user
    up = UserProfile.objects.get(user=request.user)
    nthisweek = len(Request.get_user_in_threshold(user))
    context['sent_too_many'] = nthisweek >= up.requests_per_week
    context['limit'] = up.requests_per_week
    return render_to_response(template, context, context_instance=RequestContext(request))

@login_required
def new_new_request(request, template="requests/request_wizard.html"):
    context = {}
    user = request.user
    up = UserProfile.objects.get(user=request.user)
    if up.default_request_creator_free:
        up.default_request_creator_free = False
        up.save()
    return render_to_response(template, context, context_instance=RequestContext(request))

@login_required
def free_request_edit(request, pk=None, template='requests/free_edit.html'):
    context = {}
    user = request.user
    up = UserProfile.objects.get(user=request.user)
    if not up.default_request_creator_free:
        up.default_request_creator_free = True
        up.save()
    context['is_verified'] = up.is_verified
    nthisweek = len(Request.get_user_in_threshold(user))
    context['sent_too_many'] = nthisweek >= up.requests_per_week
    context['limit'] = up.requests_per_week
    if pk is not None:
        obj = get_object_or_404(Request, id=pk)
        #TODO this is basically two lookups, one to render the page and then one to the api
        context['edit_obj'] = obj
    return render_to_response(template, context, context_instance=RequestContext(request))


@login_required
def send_request(request, pk=None):
    obj = get_object_or_404(Request, id=pk)
    can_edit = request.user.has_perm(Request.get_permission_name('edit'), obj)
    if not can_edit:
        #don't let other fools spam
        return render_to_response('403.html', {}, context_instance=RequestContext(request))
    user = request.user
    up = UserProfile.objects.get(user=request.user)
    nthisweek = len(Request.get_user_in_threshold(user))

    if not up.is_verified:
        return render_to_response('users/confirm_email.html', {'nthisweek' : nthisweek, 'limit'  : up.requests_per_week}, context_instance=RequestContext(request))
    if nthisweek >= up.requests_per_week:
        return render_to_response('requests/send_limit.html', {'nthisweek' : nthisweek, 'limit'  : up.requests_per_week}, context_instance=RequestContext(request))
    
    if not obj.sent:
        #if len(obj.get_contacts_with_email):
            #set the final version of the printed request
        obj.create_pdf_body()
        obj.send()
    rdv = RequestDetailView.as_view()
    return rdv(request=request, pk=pk)


class RequestListView(ListView):


    def post(self, request, *args, **kwargs):
        """ 
        Lets user edit settings on posts
        """

        user = self.request.user
        form = UpdateForm(self.request.POST)

        if not form.is_valid():
            return render_to_response('403.html', {}, context_instance=RequestContext(request))
            
        requests_to_modify = form.cleaned_data['requests_to_modify']
        action = form.cleaned_data['action']


        for obj in requests_to_modify:
            can_edit = user.has_perm(Request.get_permission_name('edit'), obj)
            if not can_edit:
                # Chicanery? 
                return render_to_response('403.html', {}, context_instance=RequestContext(request))

            if action == "Make Public":
                obj.private = False
            elif action == "Make Private":
                obj.private = True
            elif action == "Delete":
                obj.status = 'X'
            else:
                obj.status = form.cleaned_data['newstatus']
                if obj.status != 'F' and obj.status != 'P':
                    obj.date_fulfilled = None
                elif obj.status == 'F' or obj.status == 'P':
                    obj.date_fulfilled = datetime.now()

                #groups = form.cleaned_data['groups']
            obj.save()

        # Now use the get handler to reapply the filters
        # and pagination
        return self.get(request, *args, **kwargs)

    def get_paginate_by(self, qset):
        default_per_page = 20
        try:
            show_param = self.request.GET.get('show')
            if show_param == 'all':
                return None
            return int(self.request.GET.get('show'))
        except:
            return default_per_page

    def filter_queryset(self, queryset):
        queries = self.request.GET.copy()
        if self.request.user.username == '':
            return queryset
        form = FilterForm(self.request.user.userprofile, self.request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            if form.cleaned_data['agency']:
                queryset = queryset.filter(agency=form.cleaned_data['agency'])
            if form.cleaned_data['status'] and form.cleaned_data['status'] != 'A':
                queryset = queryset.filter(status=form.cleaned_data['status'])

            if form.cleaned_data['added_before']:
                # Need to increment this to deal with time of day issues
                queryset = queryset.filter(date_added__lte=form.cleaned_data['added_before'] + timedelta(days=1))

            if form.cleaned_data['added_after']:
                queryset = queryset.filter(date_added__gte=form.cleaned_data['added_after'])

            if form.cleaned_data['tags']:
                tags = form.cleaned_data['tags']
                for tag in tags:
                    queryset = queryset.filter(tags=tag)
            
        self.filterform = form

        if 'order_by' in queries:
            if queries['order_by'] == "due_date" or queries['order_by'] == "status" or queries['order_by'] == 'title'\
             or queries['order_by'] == "-due_date" or queries['order_by'] == "-status" or queries['order_by'] == '-title':
                return queryset.order_by(queries['order_by'])

        return queryset

    def get_context_data(self, **kwargs):
        context = ListView.get_context_data(self, **kwargs)
        # Don't use super here to avoid multiple-inheritance issues

        queries = self.request.GET.copy()

        if 'page' in queries:
            del queries['page']

        context['show_create'] = False

        queries_encoded = queries.urlencode()
        context['queries_encoded'] = queries_encoded
        if hasattr(self, 'filterform'):
            context['filterform'] = self.filterform



        return context


class LinkUserRequestListView(RequestListView):
    context_object_name = 'request_list'
    template_name = 'requests/request_list.html'

    def get_queryset(self):
        try: 
            code = self.request.GET['code']
            self.vl = vl = ViewableLink.objects.get(code=code)
            user = vl.owner
            queryset = Request.objects.for_user(user).filter(author=user).order_by('-date_added')

            for tag in vl.tags.all():
                queryset = queryset.filter(tags=tag)
            return self.filter_queryset(queryset)
        except Exception as e:
            logger.exception(e)
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(LinkUserRequestListView, self).get_context_data(**kwargs)
        context['scope'] = "Link"
        context['code'] = self.vl.code
        context['tags'] = self.vl.tags
        return context

    def filter_queryset(self, queryset):
        form = FilterForm(self.vl.owner.userprofile, self.request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            if form.cleaned_data['agency']:
                queryset = queryset.filter(agency=form.cleaned_data['agency'])

            if form.cleaned_data['added_before']:
                # Need to increment this to deal with time of day issues
                queryset = queryset.filter(date_added__lte=form.cleaned_data['added_before'] + timedelta(days=1))

            if form.cleaned_data['added_after']:
                queryset = queryset.filter(date_added__gte=form.cleaned_data['added_after'])

            # Don't need to do tags here -- we already did that
        self.filterform = form
        return queryset

    def dispatch(self, *args, **kwargs):
        return super(LinkUserRequestListView, self).dispatch(*args, **kwargs)


class UserRequestListView(RequestListView):
    """
    Main view showing the list of all user's requests. Used as an index page.
    """
    context_object_name = 'request_list'
    template_name = 'requests/request_list.html'

    def get_queryset(self):
        queryset = Request.objects.for_user(self.request.user).filter(author=self.request.user).order_by('-date_added')
        return super(UserRequestListView, self).filter_queryset(queryset)

    def get_context_data(self, **kwargs):
        context = super(UserRequestListView, self).get_context_data(**kwargs)
        context['scope'] = "My"
        context['user_tags'] = UserProfile.objects.get(user=self.request.user).tags.all()
        try:
            context['show_create'] = Request.objects.for_user(self.request.user).filter(author=self.request.user).count() <= 0
        except:
            context['show_create'] = False
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserRequestListView, self).dispatch(*args, **kwargs)


class SingleGroupRequestListView(RequestListView):
    context_object_name = 'request_list'
    template_name = 'requests/request_list.html'

    def get_queryset(self, **kwargs):
        try:
            pk = self.kwargs['pk']
            user = self.request.user
            group = user.groups.get(pk=pk)
            return get_objects_for_group(group, Request.get_permissions_path('view')).filter(~Q(status='X'))
        except:
            return Request.objects.none()

    def get_context_data(self, **kwargs):
        context = super(SingleGroupRequestListView, self).get_context_data(**kwargs)
        context['scope'] = "Group"
        try:
            pk = self.kwargs['pk']
            user = self.request.user
            group = user.groups.get(pk=pk)
            context['group'] = group
        except:
            pass
        return context

class GroupRequestListView(RequestListView):
    """
    Main view showing the list of all user's requests. Used as an index page.
    """
    context_object_name = 'request_list'
    template_name = 'requests/request_list.html'

    def get_queryset(self):
        from guardian.shortcuts import get_objects_for_user
        queryset = get_objects_for_user(self.request.user,  Request.get_permissions_path('view'))
        #queryset = Request.objects.for_user(self.request.user).filter(private=True).exclude(author=self.request.user).order_by('-date_added')
        return super(GroupRequestListView, self).filter_queryset(queryset)

    def get_context_data(self, **kwargs):
        context = super(GroupRequestListView, self).get_context_data(**kwargs)
        context['scope'] = "Group"
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GroupRequestListView, self).dispatch(*args, **kwargs)


class RequestListViewPublic(RequestListView):
    """
    Main view showing the list of top donors. Used as an index page.
    """
    context_object_name = 'request_list'
    template_name = 'requests/request_list.html'

    def get_queryset(self):
        queryset = Request.objects.for_group_a('public').order_by('-date_added')
        return super(RequestListViewPublic, self).filter_queryset(queryset)

    def get_context_data(self, **kwargs):
        context = super(RequestListViewPublic, self).get_context_data(**kwargs)
        context['scope'] = "Public"
        return context


class LinkRequestDetailView(DetailView):
    """
    Returns a specific request using the slug as the unique identifier
    and requires a code for authorization
    """
    context_object_name = 'request'
    template_name = 'requests/request_detail.html'

    def get_queryset(self):
        try:
            code = self.request.GET['code']
            self.vl = vl = ViewableLink.objects.get(code=code)

            user = vl.owner
            queryset = Request.objects.for_user(user).filter(author=user)

            for tag in vl.tags.all():
                queryset = queryset.filter(tags=tag)
            if vl.request:
                queryset = queryset.filter(id=vl.request.id)
            return queryset
        except Exception as e:
            logger.exception(e)
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(LinkRequestDetailView, self).get_context_data(**kwargs)
        context['can_edit'] = False
        mb = MailBox.objects.get_or_create(usr=self.object.author)[0]
        context['replies'] = mb.get_threads(self.object.id)
        context['can_view'] = True
        context['DEBUG'] = settings.DEBUG
        context['groups'] = get_groups_and_usergroups(self.request.user)
        context['user_tags'] = []
        editperm = Request.get_permission_name('edit')

        return context

    def dispatch(self, *args, **kwargs):
        return super(LinkRequestDetailView, self).dispatch(*args, **kwargs)

class RequestDetailView(DetailView):
    """
    Returns a specific request using the slug as the unique identifier
    """
    context_object_name = 'request'
    template_name = 'requests/request_detail.html'

    def post(self, request, *args, **kwargs):
        user = self.request.user
        form = UpdateForm(self.request.POST)

        if not form.is_valid():
            return render_to_response('403.html', {}, context_instance=RequestContext(request))

        requests_to_modify = form.cleaned_data['requests_to_modify']
        for obj in requests_to_modify:
            can_edit = user.has_perm(Request.get_permission_name('edit'), obj)
            if not can_edit:
                # Chicanery? 
                return render_to_response('403.html', {}, context_instance=RequestContext(request))
            if form.cleaned_data['newduedate']:
                obj.due_date = form.cleaned_data['newduedate']
            if form.cleaned_data['newsubject']:
                obj.title = form.cleaned_data['newsubject']
            if form.cleaned_data['newupdateddate']:
                obj.date_updated = form.cleaned_data['newupdateddate']
            if form.cleaned_data['newfulfilleddate']:
                obj.date_fulfilled = form.cleaned_data['newfulfilleddate']
            if form.cleaned_data['newstatus']:
                #allow requests to be set even if they aren't sent because not all requests can be emailed
                obj.set_status(form.cleaned_data['newstatus'])
                if obj.status != 'F' and obj.status != 'P':
                    obj.date_fulfilled = None
                elif obj.status == 'F' or obj.status == 'P' and form.cleaned_data['newfulfilleddate']:
                    obj.date_fulfilled = form.cleaned_data['newfulfilleddate']
                elif obj.status == 'F' or obj.status == 'P' and not form.cleaned_data['newfulfilleddate']:
                    obj.date_fulfilled = datetime.now(tz=pytz.utc)
                else:
                    obj.date_fulfilled = None
            if form.cleaned_data['addgroups']:
                editperm = Request.get_permissions_path('edit')
                viewperm = Request.get_permissions_path('view')
                for group in form.cleaned_data['addgroups']:
                    assign_perm(editperm, group, obj)
                    assign_perm(viewperm, group, obj)
            if form.cleaned_data['removegroups']:
                for group in form.cleaned_data['removegroups']:
                    # Can't remove the author of the request
                    if group.name != obj.author.username:
                        remove_perm('edit_this_request', group, obj)

            action = form.cleaned_data['action']
            if action == "Make Public":
                obj.private = False
            if action == "Make Private":
                obj.private = True

            obj.save()
            
        return self.get(request, *args, **kwargs)
        

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.username != '':
            return Request.objects.for_user(self.request.user)
        return Request.objects.for_group_a('public').order_by('-date_added')

    def get_context_data(self, **kwargs):
        context = super(RequestDetailView, self).get_context_data(**kwargs)
        context['can_edit'] = self.request.user.has_perm(Request.get_permission_name('edit'), self.object)

        context['show_edit_button'] =  (self.object.status == 'I' or self.object.status == 'U') and context['can_edit']

        mb = MailBox.objects.get_or_create(usr=self.object.author)[0]
        context['replies'] = mb.get_threads(self.object.id)
        context['can_view'] = self.request.user.has_perm(Request.get_permission_name('view'), self.object)
        context['DEBUG'] = settings.DEBUG
        context['groups'] = get_groups_and_usergroups(self.request.user)
        context['user_tags'] = []
        if context['can_edit']:
            context['user_tags'] = UserProfile.objects.get(user=self.request.user).tags.all()
        context['is_author'] = (self.request.user == self.object.author)
        context['provisioned_email'] = mb.get_provisioned_email()
        editperm = Request.get_permission_name('edit')
        context['contacts_sin_email'] = len(self.object.get_contacts_with_email)

        context['can_view'] = self.request.user.has_perm(Request.get_permission_name('view'), self.object)
        return context

    #@method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RequestDetailView, self).dispatch(*args, **kwargs)


def request_add_support(request, slug, user_id):
    message = ''
    supporters = Request.objects.filter(slug=slug)[0].supporters.all()
    if len(supporters) > 0:
        success = False
        message = "You already support this request. Thanks for your support!"
    else:
        logger.debug(User.objects.get(id=user_id))
        try:
            user = User.objects.get(id=user_id)
            Request.objects.get(slug=slug).supporters.add(user)
            supporters = Request.objects.get(slug=slug).supporters.all()
            success = True
            message = 'Thanks! You are now a public supporter of this request.'
        except:
            success = False
            message = 'Something went wrong (Invalid user id).'
    return render_to_response('requests/addsupport.json', {
        "success": success,
        "message": message,
        "supporters": supporters,
    }, context_instance=RequestContext(request))
