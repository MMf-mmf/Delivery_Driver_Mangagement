from django.contrib import admin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(admin.ModelAdmin):
        # add_form = CustomUserCreationForm
        # form = CustomUserChangeForm
        model = CustomUser
        list_display = [
                "email",
                "username",
                "name",
                "is_staff",
                'is_driver',
                'is_customer'
                ]
        
admin.site.register(CustomUser, CustomUserAdmin)
