from apps.contacts.models import Contact, Title, Phone, Address
from django import forms


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact


class TitleForm(forms.ModelForm):
    class Meta:
        model = Title


class PhoneForm(forms.ModelForm):
    class Meta:
        model = Phone


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
