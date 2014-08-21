import operator

from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.views.generic.detail import SingleObjectMixin

from apps.government.models import Government, Nation, Language,\
 Statute
from apps.agency.models import Agency
from apps.requests.models import Request
from apps.requests.views import RequestListView

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test



class StatuteListView(ListView):
    """
    Main view showing the list of agencies. Used as an index page.
    """
    context_object_name = 'statutes'
    template_name = 'government/statute_list.html'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Statute.objects.all_them().order_by('-created')
        else:
            return Statute.objects.all().order_by('-created')

    def get_context_data(self, **kwargs):
        context = super(StatuteListView, self).get_context_data(**kwargs)
        context['can_edit'] = self.request.user.is_staff
        #context['request_cnt'] = Request.objects.all().count()
        #context['agency_cnt'] = Agency.objects.filter(deprecated__isnull=True).count()
        return context

    def dispatch(self, *args, **kwargs):
        return super(StatuteListView, self).dispatch(*args, **kwargs)

class StatuteDetailView(RequestListView, SingleObjectMixin):
    """
    Returns a specific agency using the slug as the unique identifier
    """
    template_name = 'government/statute.html'

    def get(self, request, *args, **kwargs):
        # Need to explicitly set object since it's not a DetailView
        qs = None
        if self.request.user.is_staff:
            qs = Statute.objects.all_them().order_by('-created')
        else:
            qs = Statute.objects.all().order_by('-created')
        self.object = self.get_object(queryset = qs)
        return super(StatuteDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StatuteDetailView, self).get_context_data(**kwargs)
        context['statute'] = self.object
        contact_cnt = 0
        if self.object.get_governments:
            context['governments'] = self.object.get_governments
            context['request_cnt'] = Request.objects.filter(government=self.object.get_governments[0]).count()
            context['agency_cnt'] = Agency.objects.filter(government=self.object.get_governments[0]).count()
            for agency in Agency.objects.filter(government=self.object.get_governments[0]):
                contact_cnt += agency.contacts.filter(hidden=False).count()
        else:
            context['request_cnt'] = context['agency_cnt'] = 0
        context['contacts_cnt'] = contact_cnt
        context['can_edit'] = self.request.user.is_staff
        context['fees'] = self.object.fees_exemptions.filter(typee='F').order_by("-created")
        context['exemptions'] = self.object.fees_exemptions.filter(typee='E').order_by("-created")
        updates = self.object.updates.all().order_by("-pubbed")
        if updates.count() > 0:
            context['update'] = updates[0]
        return context

    def get_queryset(self):
        governments = self.object.get_governments
        # Bitwise or doubles as union operator for QuerySets
        requests = reduce(operator.or_, [Request.objects.for_group_a('public').filter(government__slug=government.slug) for government in governments], Request.objects.none())
        return super(StatuteDetailView, self).filter_queryset(requests)
    
    #@user_passes_test(lambda u:u.user.is_staff, login_url='/')  
    #@method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(StatuteDetailView, self).dispatch(*args, **kwargs)
