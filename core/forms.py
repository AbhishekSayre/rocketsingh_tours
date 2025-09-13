from django import forms
from .models import QuoteRequest, CustomUser, Booking, Traveler
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.password_validation import validate_password
from django.forms import DateInput








class QuoteRequestForm(forms.ModelForm):
    class Meta:
        model = QuoteRequest
        fields = ['destination', 'departure', 'name', 'phone', 'email', 'message']

        widgets = {
            'destination': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Kerala, Rajasthan, Manali...'
            }),
            'departure': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Special requests or questions...'
            }),
        }



class LoginForm(forms.Form):
    identifier = forms.CharField(label="Email or Phone")
    password = forms.CharField(widget=forms.PasswordInput)





GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'id': 'id_password1',
            'placeholder': 'Create a password',
            'class': 'form-control'
            }),
            label="Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'id': 'id_password2',
            'placeholder': 'Confirm your password',
            'class': 'form-control'
            }),
            label="Confirm Password"
    )
    terms = forms.BooleanField(required=True, label="I agree to the Terms and Conditions")
    dob = forms.DateField(
        label='Date of Birth',
        widget=DateInput(attrs={
            'type': 'date',
            'placeholder': 'YYYY-MM-DD',
            'class': 'form-control'
            })
    )

    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'phone', 'gender', 'dob']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter your full name',
                'class': 'form-control',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email',
                'class': 'form-control',
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Enter your phone number',
                'class': 'form-control',
            }),
            'gender': forms.Select(attrs={
                'placeholder': 'Gender',
                'class': 'form-control',
             }),
           
            'dob': forms.DateInput(attrs={
                'placeholder': 'YYYY-MM-DD',
                'class': 'form-control',
                'type': 'date',
            }),
                    }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if CustomUser.objects.filter(phone=phone).exists():
            raise ValidationError("This phone number is already registered.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                self.add_error('password2', "Passwords do not match.")
            else:
                validate_password(password1)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
    


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'phone', 'dob', 'gender']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'phone', 'dob', 'gender', 'profile_photo']
        


class TravelerForm(forms.ModelForm):
    class Meta:
        model = Traveler
        fields = ['name', 'age', 'email', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Age'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone'}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['special_request']
        widgets = {
            'special_request': forms.Textarea(attrs={
                'placeholder': 'Special Request',
                'rows': 2
            }),
        }

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileCompletionForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "gender", "dob", "phone"]  # adjust to your actual field names
        widgets = {
            "dob": forms.DateInput(attrs={"type": "date"}),
        }
