from django import forms
from django.forms import extras
from datetime import datetime

class Register(forms.Form):
    years_to_display = range(datetime.now().year - 100, datetime.now().year + 1)
    first_name = forms.CharField(
        label = "First Name", 
        max_length = 45,
        min_length = 2, 
        widget = forms.TextInput(
            attrs = {
                "class": "form-control", 
                "placeholder": "Your first name",
            }
        )
    )
    last_name = forms.CharField(
        label="Last Name", 
        max_length=45, 
        min_length = 2, 
        widget=forms.TextInput(
            attrs={
                "class": "form-control", 
                "placeholder": "Your last name",
            }
        )
    )
    email = forms.EmailField(
        label = "Email", 
        max_length = 45, 
        widget = forms.TextInput(
            attrs = {
                "class": "form-control", 
                "placeholder": "Your email",
            }
        )
    )
    password = forms.CharField(
        label = "Password", 
        max_length = 45,
        min_length = 8,  
        widget = forms.PasswordInput(
            attrs = {
                "class": "form-control", 
                "placeholder": "Your password",
            }
        )
    )
    cpassword = forms.CharField(
        label = "Confirm Password", 
        max_length = 45, 
        widget = forms.PasswordInput(
            attrs = {
                "class": "form-control", 
                "placeholder": "Your password",
            }
        )
    )
    birthday = forms.DateField(
        widget = extras.SelectDateWidget (
            years = years_to_display, 
            attrs = {
                "class": "form-control", 
                "placeholder": "Your birthdate",
            }
        )
    )

class Login(forms.Form):
    email = forms.EmailField(
        label = "Email", 
        max_length = 45, 
        widget = forms.TextInput(
            attrs = {
                "class": "form-control", 
                "placeholder": "Your email",
            }
        )
    )
    password = forms.CharField(
        label = "Password", 
        max_length = 45,
        min_length = 8,  
        widget = forms.PasswordInput(
            attrs = {
                "class": "form-control", 
                "placeholder": "Your password",
            }
        )
    )
