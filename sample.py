import email
import imp
from django import forms
from app.model.client import Client


# creating a form
class ClientForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Client Name"}),
    )
    parent_company = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "input", "placeholder": "Parent Company Name"}
        ),
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "textarea",
                "style": "height: 10em;",
                "placeholder": "Address",
            }
        ),
    )
    contact = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Contact"}),
    )
    email = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Email"}),
    )
    gst_in = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "GSTIN"}),
    )
    pan = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "PAN"}),
    )
    # create meta class
    class Meta:
        # specify model to be used
        model = Client

        # specify fields to be used
        fields = [
            "name",
            "parent_company",
            "address",
            "contact",
            "email",
            "gst_in",
            "pan",
        ]
