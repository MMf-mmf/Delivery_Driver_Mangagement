from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from .forms import CustomUserCreationForm,  EditCustomerForm, EditDriverForm, CreateDriverForm, CreateCustomerForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from .models import CustomUser
from django.views.generic import View
from django.contrib import messages


class AdminOrStaff(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    
    
    
# class SignUpView(AdminOrStaff, generic.CreateView ):
#     form_class = CustomUserCreationForm
#     success_url = reverse_lazy("login")
#     template_name = "registration/signup.html"
    
    

class CustomerListView(generic.ListView, AdminOrStaff):
    model = CustomUser
    context_object_name = 'customer_list' # this is also overriding a variable name
    queryset = CustomUser.customer_objects.all()
    template_name = "user_actions/customer_list.html"

    def get_context_data(self, **kwargs): # agin overriding the context variable in the ListView class
        # Call the base implementation first to get the context
        context = super(CustomerListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['customer_detail_url'] = 'accounts/customer/'
        return context
    
class CustomerDetailView(AdminOrStaff, SuccessMessageMixin):
    def get(self, request, pk):
        user_query_result = get_object_or_404(CustomUser, pk=pk)
        edit_user_form = EditCustomerForm(initial={
                                'username': user_query_result.username,
                                'email': user_query_result.email,
                                'business_name': user_query_result.business_name,
                                'address': user_query_result.address,
                                'contact_name': user_query_result.contact_name,
                                'phone_number': user_query_result.phone_number,
                                'contact_number': user_query_result.contact_number,
                                'latitude': user_query_result.latitude,
                                'longitude': user_query_result.longitude,
                                'comments': user_query_result.comments,
                                })
        return render(request, 'user_actions/customer_detail.html', {'edit_user_form': edit_user_form,'user_query_result': user_query_result, 'id': pk})
    
    def post(self, request, pk):
        user_query_result = get_object_or_404(CustomUser, pk=pk)
        edit_user_form = EditCustomerForm(request.POST) # this is where we bind the form to the form response i.e the error messages and the prev data
        if edit_user_form.is_valid():
            # edit_user_form.save() # if the form would be a forms.ModelForm then we would have aces to that method
            user_query_result.username = edit_user_form.cleaned_data['username']
            user_query_result.email = edit_user_form.cleaned_data['email']
            user_query_result.business_name = edit_user_form.cleaned_data['business_name']
            user_query_result.address = edit_user_form.cleaned_data['address']
            user_query_result.contact_name = edit_user_form.cleaned_data['contact_name']
            user_query_result.contact_number = edit_user_form.cleaned_data['contact_number']
            user_query_result.phone_number = edit_user_form.cleaned_data['phone_number']
            user_query_result.latitude = edit_user_form.cleaned_data['latitude']
            user_query_result.longitude = edit_user_form.cleaned_data['longitude']
            user_query_result.comments = edit_user_form.cleaned_data['comments']
            user_query_result.save()
            messages.success(request, 'Profile was updated successfully!', extra_tags='alert')
            return redirect('customer_detail', pk)
        messages.error(request, 'Error Updating Data', extra_tags='alert')
        return render(request, 'user_actions/customer_detail.html', {'edit_user_form': edit_user_form,'user_query_result': user_query_result, 'id': pk})
    
class DriverListView(AdminOrStaff):
    def get(self, request):
        drivers = CustomUser.driver_objects.all()
        return render(request, 'user_actions/drivers_list.html', {'drivers': drivers, 'driver_detail_url': 'accounts/driver/'})

class DriverDetailView(AdminOrStaff):
    def get(self, request, pk):
        driver = get_object_or_404(CustomUser, pk=pk)
        driver_form = EditDriverForm(initial={'username': driver.username, 'email': driver.email, 'is_driver': driver.is_driver, 'phone_number': driver.phone_number})
        return render(request, 'user_actions/driver_detail.html', {'driver_form': driver_form, 'id': pk})
    
    def post(self, request, pk):
        driver = get_object_or_404(CustomUser, pk=pk)
        driver_form = EditDriverForm(request.POST)
        if driver_form.is_valid():
            driver.username = driver_form.cleaned_data['username']
            driver.email = driver_form.cleaned_data['email']
            driver.phone_number = driver_form.cleaned_data['phone_number']
            driver.save()
            messages.success(request, 'Profile was updated successfully!', extra_tags='alert')
            return redirect('driver_detail', pk)
        
        messages.error(request, 'Error Updating Data', extra_tags='alert')
        return render(request, 'user_actions/driver_detail.html', {'driver_form': driver_form, 'id': driver.id})
    
    
class DeleteUserView(AdminOrStaff):
    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.delete()
        messages.success(request, 'User Successfully deleted', extra_tags='alert')
        return redirect('home')
        
class CreateDriver(AdminOrStaff):
    
        def get(self, request):
            create_driver_form = CreateDriverForm()
            return render(request, 'user_actions/create_driver.html', {'create_driver_form':create_driver_form})
        
        def post(self, request):
            # capture form
            create_driver_form = CreateDriverForm(request.POST)
            if create_driver_form.is_valid():
                username = create_driver_form.cleaned_data['username']
                phone_number = create_driver_form.cleaned_data['phone_number']
                password = create_driver_form.cleaned_data['password']
                email = create_driver_form.cleaned_data['email']
                driver = CustomUser.objects.create_user(username=username, phone_number=phone_number, email=email, password=password ,is_driver=True)
                messages.success(request, 'successfully created driver', extra_tags='alert')
                return redirect('drivers')
            messages.error(request, 'Error Creating Driver', extra_tags='alert')
            return render(request, 'user_actions/create_driver.html', {'create_driver_form':create_driver_form})
    
    
class CreateCustomer(AdminOrStaff):
    
    def get(self, request):
        create_customer_form = CreateCustomerForm()
        return render(request, 'user_actions/create_customer.html', {'create_customer_form': create_customer_form})
    
    def post(self, request):
        create_customer_form = CreateCustomerForm(request.POST)
        if create_customer_form.is_valid():
            username = create_customer_form.cleaned_data['username']
            email = create_customer_form.cleaned_data['email']
            business_name = create_customer_form.cleaned_data['business_name']
            address = create_customer_form.cleaned_data['address']
            contact_name = create_customer_form.cleaned_data['contact_name']
            phone_number = create_customer_form.cleaned_data['phone_number']
            contact_name = create_customer_form.cleaned_data['contact_name']
            latitude = create_customer_form.cleaned_data['latitude']
            longitude = create_customer_form.cleaned_data['longitude']
            comments = create_customer_form.cleaned_data['comments']
            CustomUser.objects.create_user(
                                      is_customer=True,
                                      username=username,
                                      email=email,
                                      business_name=business_name,
                                      address=address,
                                      contact_name=contact_name,
                                      phone_number=phone_number,
                                      latitude=latitude,
                                      longitude=longitude,
                                      comments=comments,
                                      )
            messages.success(request, 'successfully created Customer', extra_tags='alert')
            return redirect('customers')
        messages.error(request, 'successfully created Customer', extra_tags='alert')
        return render(request, 'user_actions/create_customer.html', {'create_customer_form': create_customer_form})