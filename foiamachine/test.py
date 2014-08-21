from apps.requests.models import Request
from apps.agency.models import Agency

a = Agency.objects.all()[0]


print a.average_time_outstanding
