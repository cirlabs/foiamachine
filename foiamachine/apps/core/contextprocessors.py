from apps.users.models import UserProfile

def default_request_form(request):
    try:
        return {
            'default_request_creation_free': UserProfile.objects.get(user=request.user).default_request_creator_free
        }
    except:
        return {
            'default_request_creation_free': False 
        }