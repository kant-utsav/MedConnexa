from django import forms
from .models import Doctor, Review
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['name', 'specialty', 'clinic_address', 'experience_years', 'bio', 'photo']

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1, max_value=5,
        widget=forms.HiddenInput()  # Use JS stars in your template
    )
    class Meta:
        model = Review
        fields = ['reviewer_name', 'rating', 'comment']   # All fields exist in Review model

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
