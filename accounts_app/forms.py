from django.core.validators import RegexValidator
from django import forms
from django.contrib.auth import get_user_model # this is the same as referencing CustomUser directly
from django.utils.translation import gettext_lazy
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser



class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(max_length=50,  help_text="no white spaces / one word")
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email', 'is_driver','is_customer',)



class CustomUserChangeForm(UserCreationForm):
    username = forms.CharField(max_length=50,  help_text="no white spaces / one word")
    class Meta:
        model = get_user_model()
        fields = ('email', 'username',)



class EditCustomerForm(forms.Form):
    username = forms.CharField(max_length=50,  help_text="no white spaces / one word")
    email = forms.EmailField()
    business_name = forms.CharField()
    address = forms.CharField()
    contact_name = forms.CharField()
    contact_number = forms.CharField(max_length=15,required=False)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = forms.CharField(validators=[phone_regex], max_length=17)
    latitude =  forms.CharField()
    longitude =  forms.CharField()
    comments =  forms.CharField(required=False)
    

    
    # def clean_username(self):
    #     data = self.cleaned_data['username']
    #     if len(data) < 2:
    #         raise ValidationError(gettext_lazy("Username is to short (min 2 characters)"))
        
    #     return data

class CreateDriverForm(forms.ModelForm):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = forms.CharField(validators=[phone_regex], max_length=17)
    class Meta:
        model = CustomUser
        fields = ['username', 'phone_number', 'password', 'email']
       
        
class EditDriverForm(forms.Form):
    username = forms.CharField(required=True, max_length=50)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=True, max_length=15)
    # class Meta:
    #     model = CustomUser
    #     fields = ['username', 'email', 'phone_number']
        

class CreateCustomerForm(forms.ModelForm):
    comments =  forms.CharField(required=False)
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'business_name', 'address', 'contact_name', 'phone_number', 'contact_name', 'contact_number', 'latitude', 'longitude', 'comments']

