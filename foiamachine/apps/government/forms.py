from apps.government.models import Language, AdminName, Nation,\
    Statute, Government
from django import forms


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language


class AdminNameForm(forms.ModelForm):
    class Meta:
        model = AdminName


class NationForm(forms.ModelForm):
    class Meta:
        model = Nation


class StatuteForm(forms.ModelForm):
    class Meta:
        model = Statute


class GovernmentForm(forms.ModelForm):
    class Meta:
        model = Government