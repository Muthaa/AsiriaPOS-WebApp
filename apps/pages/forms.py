from django import forms
import re

class RegistrationForm(forms.Form):
    storename = forms.CharField(max_length=100, required=True)
    client_name = forms.CharField(max_length=100, required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True)
    address = forms.CharField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirmation = forms.CharField(widget=forms.PasswordInput, required=True)
    

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')
        email = cleaned_data.get('email')
        phone_number = cleaned_data.get('phone_number')

        # Password match
        if password and password_confirmation and password != password_confirmation:
            self.add_error('password_confirmation', 'Passwords do not match.')

        # Email regex (Django's EmailField already does basic validation, but you can add more)
        email_regex = r'^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$'
        if email and not re.match(email_regex, email):
            self.add_error('email', 'Enter a valid email address.')

        # Phone number regex (example: only digits, 10-15 characters)
        phone_regex = r'^\+?\d{10,15}$'
        if phone_number and not re.match(phone_regex, phone_number):
            self.add_error('phone_number', 'Enter a valid phone number (10-15 digits, may start with +).')

        return cleaned_data

    def field_css_class(self, field_name):
        if self.errors.get(field_name):
            return 'form-control is-invalid'
        return 'form-control' 

class LoginForm(forms.Form):
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),
        required=True
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Phone number regex (example: only digits, 10-15 characters)
        phone_regex = r'^\+?\d{10,15}$'
        if not re.match(phone_regex, phone_number):
            raise forms.ValidationError('Enter a valid phone number (10-15 digits, may start with +)')
        return phone_number

    # Note: Some APIs might expect 'username' instead of 'phone_number'
    # If the API expects different field names, update the view accordingly 