from django import forms
from apps.doccloud.models import Document


class DocCloudDocForm(forms.ModelForm):
    class Meta:
        model = Document