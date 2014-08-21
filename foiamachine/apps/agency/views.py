from django.views.generic import ListView, DetailView
from django.views.generic.detail import SingleObjectMixin

from apps.requests.models import Request
from apps.agency.models import Agency
from apps.requests.views import RequestListView


class AgencyListView(ListView):
    """
    Main view showing the list of agencies. Used as an index page.
    """
    context_object_name = 'agency_list'
    template_name = 'agency/agency_contacts.html'
    queryset = Agency.objects.all()

class AgencyDetailView(RequestListView, SingleObjectMixin):
    """
    Returns a specific agency using the slug as the unique identifier
    """
    context_object_name = 'agency'
    template_name = 'agency/agency.html'
    queryset = Agency.objects.all()

    def get(self, request, *args, **kwargs):
        # Need to explicitly set object since it's not a DetailView
        self.object = self.get_object(queryset = Agency.objects.all())
        return super(AgencyDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AgencyDetailView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        queryset =  Request.objects.for_group_a('public').filter(agency__slug=self.object.slug)
        return super(AgencyDetailView, self).filter_queryset(queryset)

    def dispatch(self, *args, **kwargs):
        return super(AgencyDetailView, self).dispatch(*args, **kwargs)
