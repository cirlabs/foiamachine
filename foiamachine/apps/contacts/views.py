from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from apps.contacts.models import Contact
from apps.contacts.forms import ContactForm


@login_required
def create_contact(request, pk, template_name='contacts/create-contact.html'):
    context = {}
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            #get other forms as well
            contact.save()
            return render_to_response(template_name, context, context_instance=RequestContext(request))
        else:
            try:
                '''
                do error handling
                if 'email' in form.errors.keys():
                    ip = get_object_or_404(InterestedParty, email=request.POST['email'])
                    ip.followed_request.add(obj)
                    return render_to_response(template_name, context, context_instance=RequestContext(request))
                '''
                pass
            except Exception as e:
                pass
            return render_to_response(template_name, context, context_instance=RequestContext(request))
    context['contact_form'] = ContactForm()
    return render_to_response(template_name, context, context_instance=RequestContext(request))
