from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from apps.doccloud.forms import DocCloudDocForm
from apps.doccloud.models import DocumentCloudProperties, Document
from apps.requests.models import Request
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def create(request, requestpk=None, template_name='doccloud/upload.html'):
    context = {}
    context['form'] = DocCloudDocForm()
    context['pk'] = requestpk
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def list(request, template_name='doccloud/list.html'):
    context = {}
    context['objects'] = Document.objects.all()
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def detail(request, slug, template_name='doccloud/detail.html'):
    context = {}
    context['document'] = get_object_or_404(Document, slug=slug)
    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
def upload(request, requestpk=None, template_name='doccloud/list.html'):
    context = {}
    try:
        if request.method == 'POST':
            dc_form = DocCloudDocForm(request.POST, request.FILES)
            dc_form.user = request.user
            if dc_form.is_valid():
                model = dc_form.save(commit=False)
                model.user = request.user
                model.connect_dc_doc()
                model.save()

                if requestpk != None:
                    req = get_object_or_404(Request, pk=requestpk)
                    req.documents.add(model)
                    return redirect('request_detail', pk=requestpk)
            else:
                context['form'] = dc_form
                return render_to_response('doccloud/upload.html', context, context_instance=RequestContext(request))
        else:
            return render_to_response('doccloud/upload.html', context, context_instance=RequestContext(request))
    except Exception as e:
        print e#need logger
    context['objects'] = Document.objects.all()
    return render_to_response(template_name, context, context_instance=RequestContext(request))