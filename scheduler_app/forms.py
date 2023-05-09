from django import forms
from .models import Vehicle, Schedule, ScheduleStop, RouteStop, Route
from accounts_app.models import CustomUser

class CreateVehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = '__all__'

class UpdateVehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = '__all__'
        
class DateInput(forms.DateInput):
    input_type = 'date'
    
class CreateScheduleForm(forms.ModelForm):
    driver = forms.ModelChoiceField(queryset = CustomUser.driver_objects.all())
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    route_name = forms.ModelChoiceField(queryset=Route.objects.all())
    class Meta:
        model = Schedule
        # fields = '__all__'
        exclude = ('last_eta_update_timestamp',)
        widgets = {
                'dateField': DateInput
            }
        
        
class ScheduleDetailForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['route_name'].initial = 'my_initial'
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))    
    driver = forms.ModelChoiceField(queryset = CustomUser.driver_objects.all())
    class Meta:
        model = Schedule
        # fields = '__all__'
        exclude = ('last_eta_update_timestamp',)
        
class ScheduleStopForm(forms.ModelForm):
    customer = forms.ModelChoiceField(queryset= CustomUser.customer_objects.all())
    
    class Meta:
        model = ScheduleStop
        # fields = '__all__'
        exclude = ('schedule','stop_number', 'eta',)

class AddScheduleStop(forms.ModelForm):
    customer = forms.ModelChoiceField(queryset= CustomUser.customer_objects.all())
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))    
    class Meta:
        model = ScheduleStop
        #exclude = ('schedule','stop_number', 'heavy_bag', 'no_papers', 'no_bags', 'received_packages', 'received_palets', 'received_bags')
        fields = ['customer', 'status', 'start_time', 'note', 'expected_palets', 'expected_bags', 'expected_packages']
        
class CreateRouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['name']
        
class CreateRouteStopForm(forms.ModelForm):
    customer = forms.ModelChoiceField(queryset= CustomUser.customer_objects.all())
    class Meta:
        model = RouteStop
        fields = ['customer', 'general_note']
        

class FeedbackFrom(forms.ModelForm):
    received_bags = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'pickup_count'}), choices=ScheduleStop.BAGS_PAYLOAD,)
    received_palets = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'pickup_count'}), choices=ScheduleStop.PALETS_PAYLOAD,)
    feedback_note = forms.CharField(widget=forms.TextInput(attrs={'class': 'feedback_note'}), required=False)
    class Meta:
        model = ScheduleStop
        fields = ['feedback_note', 'received_bags', 'received_palets', 'heavy_bag', 'no_papers', 'no_bags', 'image']

class DriverProfileForm(forms.Form):
    username = forms.CharField(max_length=50)
    phone_number = forms.CharField()