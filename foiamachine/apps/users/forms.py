from django import forms
from apps.users.models import InterestedParty
from registration.forms import RegistrationFormUniqueEmail
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import pytz

zones = pytz.common_timezones
zones = [z for z in zones if z.startswith('US')] + [z for z in zones if not z.startswith('US')]


class UsernameOrEmailAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=512)

    def clean(self):

        try:
            result =  super(UsernameOrEmailAuthenticationForm, self).clean()
            return result
        except forms.ValidationError as ve:
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')

            # Try username as email address
            try:
                user = User.objects.get(email=username)
                email_username = user.username

                self.user_cache = authenticate(username=email_username, password=password)

                if self.user_cache is None:
                    raise ve
            except:
                raise ve

class UserRegistrationForm(RegistrationFormUniqueEmail):
    first_name = forms.CharField(max_length=512)
    last_name = forms.CharField(max_length=512)
    #organization = forms.CharField(max_length=255, required=False)
    journalist = forms.BooleanField(required=False)
    timezone = forms.ChoiceField(choices=[(x, x) for x in zones])

    mailing_address = forms.CharField(max_length=150, required=False)
    mailing_city = forms.CharField(max_length=50, required=False)
    mailing_state = forms.CharField(max_length=20, required=False)
    mailing_zip = forms.CharField(max_length=20, required=False)
    phone = forms.CharField(max_length=20, required=False)

class InterestedPartyForm(forms.ModelForm):
    class Meta:
        model = InterestedParty
        exclude = ('activation_key', 'activated_on', 'followed_request',)
