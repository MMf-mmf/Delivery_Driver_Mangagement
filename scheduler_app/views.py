import datetime
from django.conf import settings
from django.utils import timezone
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from .models import CustomUser
from .models import Vehicle, Schedule, ScheduleStop, Route, RouteStop
from .forms import ( CreateVehicleForm, UpdateVehicleForm,
                    CreateScheduleForm, ScheduleStopForm,
                    CreateRouteForm, CreateRouteStopForm,
                    ScheduleDetailForm, AddScheduleStop,
                    FeedbackFrom, DriverProfileForm,
                    )
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from concurrent.futures import ThreadPoolExecutor
from .helpers.google_api import fetch_stop_etas, fetch_stop_etas_for_routes
from .helpers.twilio_api import send_gps_error_message


class AdminOrStaff(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    
    
class CreateVehicleView(AdminOrStaff):
    def get(self, request):
        create_vehicle_form = CreateVehicleForm()
        return render(request, 'create_vehicle.html', {'create_vehicle_form': create_vehicle_form})
    def post(self, request):
        create_vehicle_form = CreateVehicleForm(request.POST, request.FILES)
   
        if create_vehicle_form.is_valid():
            name = create_vehicle_form.cleaned_data['name']
            make = create_vehicle_form.cleaned_data['make']
            model = create_vehicle_form.cleaned_data['model']
            year = create_vehicle_form.cleaned_data['year']
            image = create_vehicle_form.cleaned_data['image']
            capacity = create_vehicle_form.cleaned_data['capacity']
            lift_gate = create_vehicle_form.cleaned_data['lift_gate']
            Vehicle.objects.create(name=name, make=make, model=model, year=year, image=image, capacity=capacity, lift_gate=lift_gate)
            messages.success(request, 'Profile was updated successfully!', extra_tags='alert')
            return redirect('vehicles')
        return render(request, 'create_vehicle.html', {'create_vehicle_form': create_vehicle_form})
    
    
class VehicleListView(AdminOrStaff):
    def get(self, request):
        vehicles = Vehicle.objects.all()
        return render(request, 'vehicle_list.html', {'vehicles': vehicles})
        
class VehicleDetailView(AdminOrStaff):
    def get(self, request, pk):
        vehicle = get_object_or_404(Vehicle, pk=pk)
        update_vehicle_form = UpdateVehicleForm(initial={'name': vehicle.name, 'make': vehicle.make, 'model': vehicle.model, 'year': vehicle.year, 'image': vehicle.image, 'capacity': vehicle.capacity, 'lift_gate': vehicle.lift_gate})
        return render(request, 'vehicle_detail.html', {'vehicle': vehicle, 'update_vehicle_form': update_vehicle_form, 'pk': pk})
    def post(self, request, pk):
        vehicle = get_object_or_404(Vehicle, pk=pk)
        form = CreateVehicleForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile was updated successfully!', extra_tags='alert')
            return redirect('vehicle_detail', pk)
        return render(request, 'create_vehicle.html', {'create_vehicle_form': form, 'pk': pk})
    
@login_required()  
def delete_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    vehicle.delete()
    messages.success(request, 'User Successfully deleted', extra_tags='alert')
    return redirect('vehicles')


class CreateScheduleView(AdminOrStaff):
    def get(self, request):
        
        today = datetime.date.today()
        threePm = datetime.time(hour=15)
        today_three_pm = datetime.datetime.combine(today, threePm)
        form = CreateScheduleForm(initial={'start_time': today_three_pm})
        return render(request, 'create_schedule.html', {'form': form})
    
    def post(self, request):
        form = CreateScheduleForm(request.POST)
        if form.is_valid():
            driver = form.cleaned_data['driver']
            vehicle = form.cleaned_data['vehicle']
            route_name = form.cleaned_data['route_name']
            start_time = form.cleaned_data['start_time']
            total_palets = form.cleaned_data['total_palets']
            total_bags =  form.cleaned_data['total_bags']
            total_packages = form.cleaned_data['total_packages']
            schedule = Schedule.objects.create(driver=driver, vehicle=vehicle, route_name=route_name.name, start_time=start_time, total_palets=total_palets, total_bags=total_bags, total_packages=total_packages)
            # get all stops we want to create a ScheduleStop object for each
            route = Route.objects.get(name=route_name.name)
            stops = route.routestop_set.all().order_by('stop_number')
            with transaction.atomic():
                for stop in stops:
                    ScheduleStop.objects.create(
                        schedule=schedule,
                        customer=stop.customer,
                        stop_number=stop.stop_number,
                        eta=stop.eta,
                        note=stop.general_note,
                    )
        # should redirect if successfully created
            messages.success(request, 'Schedule was successfully created!', extra_tags='alert')
            return redirect('schedules')
        messages.error(request, 'Schedule was successfully created!', extra_tags='alert')
        return render(request, 'create_schedule.html', {'form': form})
    
    
@login_required()    
def delete_schedule(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    schedule.delete()
    messages.success(request, 'stop Successfully deleted', extra_tags='alert')
    return redirect('schedules')

class ScheduleListView(AdminOrStaff):
    def get(self, request):
        # in_progress_schedules = Schedule.objects.filter(status="IP")
        all_schedules = Schedule.objects.all()
        return render(request, 'schedule_list.html', {'all_schedules': all_schedules})
    
    
class AddScheduleStopView(AdminOrStaff):
    def get(self, request, pk):
        today = datetime.date.today()
        elevenAm = datetime.time(hour=15)
        today_eleven_am = datetime.datetime.combine(today, elevenAm)

        form = AddScheduleStop(initial={'start_time': today_eleven_am})
        return render(request, 'add_schedule_stop.html', {'form': form})
    
    def post(self, request, pk):
        form = AddScheduleStop(request.POST)
        if form.is_valid():
            schedule = get_object_or_404(Schedule, pk=pk)
            # find the last stop number so we can create the new schedule stop with a stop number that is not in use
            query = schedule.schedulestop_set.all()
           
            if not query:
                stop_number = 1
            else:  
                stop_number = query.order_by('stop_number').last().stop_number
                stop_number += 1
            customer = form.cleaned_data['customer']
            status = form.cleaned_data['status']
            start_time =  form.cleaned_data['start_time']
            note = form.cleaned_data['note']
            expected_bags = form.cleaned_data['expected_bags']
            expected_packages = form.cleaned_data['expected_packages']
            expected_palets = form.cleaned_data['expected_palets']
            new_stop = ScheduleStop.objects.create(
                schedule=schedule,
                customer=customer,
                stop_number=stop_number,
                start_time=start_time,
                note=note,
                status=status,
                expected_bags=expected_bags,
                expected_packages=expected_packages,
                expected_palets=expected_palets
                )
           
            if new_stop:
                messages.success(request, 'Stop successfully added', extra_tags='alert')
                return redirect('schedule_detail', pk)
        return render(request, 'add_schedule_stop.html', {'form': form})
       
       
@login_required
def updateScheduleStopEtas(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    # if the schedule is complete send htmx the 286 response to stop it auto fetching agin
    if schedule.status == 'FN':
        return HttpResponse(status=286)
        
    # get stops to calculate eta
    all_stops = ScheduleStop.objects.filter(schedule_id=pk).order_by('stop_number')
    drivers_latitude = schedule.driver.latitude
    drivers_longitude = schedule.driver.longitude
    all_etas = {}
    errors = []
    departure_time = datetime.datetime.now()
    with ThreadPoolExecutor(max_workers=10) as executor:
        for stop_number, stop in enumerate(all_stops):
            if (stop.status == 'IC'):
                executor.submit(fetch_stop_etas, all_stops, stop_number, drivers_latitude, drivers_longitude, all_etas, departure_time, errors)
            else:
                all_etas[stop_number + 1] = 0
        if len(errors) > 0:
            messages.error(request, f'{errors[0]}', extra_tags='alert')
        else:
            if all_etas:
                # loop over the all_etas and make add the prev stops time to the eta of a later stop
                for i in range(1, len(all_etas) + 1):
                    if i > 2:
                        all_etas[i] = (all_etas[i-1] + all_etas[i]) 
                # we updated the data base with the new eta's for every stop
                for stop in all_stops:
                    stop_object = ScheduleStop.objects.get(id=stop.id)
                    stop_object.eta = all_etas[stop_object.stop_number]
                    stop_object.save()  
                schedule.last_eta_update_timestamp = now
                schedule.save()     
                messages.success(request, 'Successfully Updated Etas for route stops', extra_tags='alert')
   
    all_stops = ScheduleStop.objects.filter(schedule_id=pk).order_by('stop_number')
    return render(request, 'partials/schedule_stop_list.html', {'all_stops': all_stops, 'id':pk})


        
   
class ScheduleDetailView(AdminOrStaff):
    def get(self, request, pk):
        # FIRST STEP IS TO WRITE A QUERY TO FIND ALL THE STOPS ASSOCIATED WITH A GIVEN SCHEDULE AND GET THE INFO AND THE RELATED STOP INFO
        schedule = get_object_or_404(Schedule, pk=pk)
        key = settings.GOOGLE_API_KEY
        drivers_latitude = schedule.driver.latitude
        drivers_longitude = schedule.driver.longitude
        position_timestamp = schedule.driver.position_timestamp # last time the drivers location was updated
        schedule_form = ScheduleDetailForm(initial={
                                                    'driver': schedule.driver,
                                                    'vehicle': schedule.vehicle,
                                                    'route_name': schedule.route_name,
                                                    'start_time': schedule.start_time,
                                                    'status': schedule.status,
                                                    'total_palets': schedule.total_palets,
                                                    'total_bags': schedule.total_bags,
                                                    'total_packages': schedule.total_packages,
                                                    })
        all_stops = schedule.schedulestop_set.all().order_by('stop_number')
        # get route eta's from scheduloe stop model if the stop is
        # 1) if schedule is complete skip
        # 2) if schedule is not started get eta from schedule stops felids ( that have bean set when the route was created)
        # 3) if the schedule is in progress ask google for a updated eta for the incomplete routs
        all_etas = {}
        errors = []
        now = timezone.now()
        five_min_ago = now - datetime.timedelta(minutes=5) # this should be 5 min
        updated = schedule.last_eta_update_timestamp
        # if updated has a smaller valued then five min ago we want to get a new eta
        # breakpoint()
        if ((schedule.status == 'IP') and (updated < five_min_ago)) and schedule.start_time == datetime.date.today():
            departure_time = datetime.datetime.now()
            with ThreadPoolExecutor(max_workers=10) as executor:
                for stop_number, stop in enumerate(all_stops):
                    if (stop.status == 'IC'): # ic == incomplete
                        executor.submit(fetch_stop_etas, all_stops, stop_number, drivers_latitude, drivers_longitude, all_etas, departure_time, errors)
                    else:
                        all_etas[stop_number + 1] = 0
            # loop over the all_etas and make add the prev stops time to the eta of a later stop
            if len(errors) > 0:
                messages.error(request, f'{errors[0]}', extra_tags='alert')
            else:
              
                for i in range(1, len(all_etas) + 1):
                    if i != 1:
                        all_etas[i] = (all_etas[i-1] + all_etas[i]) 

                # we updated the data base with the new eta's for every stop
                for stop in all_stops:
                    stop_object = ScheduleStop.objects.get(id=stop.id)
                    stop_object.eta = all_etas[stop_object.stop_number]
                    stop_object.save()
                    
                # after we update the etas we mark that schedule as having updated etas with a timestamp
                schedule.last_eta_update_timestamp = now
                schedule.save()
           
        total_stops_count = range(1, all_stops.count() + 1)
     
        return render( request, 'schedule_detail.html', 
                    {
                        'schedule': schedule,
                        'all_stops': all_stops,
                        'total_stops_count': total_stops_count,
                        'id': pk,
                        'schedule_form':schedule_form,
                        'key': key,
                        'drivers_latitude': drivers_latitude,
                        'drivers_longitude': drivers_longitude,
                        'position_timestamp': position_timestamp,
                    })

    def post(self, request, pk):
        schedule = get_object_or_404(Schedule, pk=pk)
        all_stops = schedule.schedulestop_set.all()
        total_stops_count = range(1, all_stops.count() + 1)
       
        schedule_form = ScheduleDetailForm(request.POST, request.FILES, instance=schedule)
        if schedule_form.is_valid():
            schedule_form.save()
            messages.success(request, 'Successfully Updated Schedule', extra_tags='alert')
            return redirect('schedule_detail', pk)
        messages.error(request, 'Error Updating Data', extra_tags='alert')
        return render( request, 'schedule_detail.html', 
                                    {
                                    'schedule': schedule,
                                    'all_stops': all_stops,
                                    'total_stops_count': total_stops_count,
                                    'id': pk,
                                    'schedule_form':schedule_form, 
                                    }
                        )
        
        
class DriverScheduleLocation(AdminOrStaff):
    def get(self, request, pk):
        schedule = get_object_or_404(Schedule, id=pk)
        lat = schedule.driver.latitude
        lon = schedule.driver.longitude
        return JsonResponse({'lat': lat, 'lon': lon}) 
    
    
@login_required()         
def sort_schedule_stop(request, pk):
    stop_ids_in_order = request.POST.getlist('stop_ids_in_order')
    all_stops = []
    with transaction.atomic():
        #loop over all stop id's from the form
        # all_stops = ScheduleStop.objects.filter(schedule=pk)
        for index, stop_id in enumerate(stop_ids_in_order, start=1):
            stop = ScheduleStop.objects.get(id=stop_id)
            stop.stop_number = index
            stop.eta = None
            stop.save()
            all_stops.append(stop)
    return render(request, 'partials/schedule_stop_list.html', {'all_stops': all_stops, 'id': pk})

def sort_route_stop(request):
    stop_ids_in_order = request.POST.getlist('stop_ids_in_order')
    all_stops = []
    with transaction.atomic():
        for index, stop_id in enumerate(stop_ids_in_order, start=1):
            stop = RouteStop.objects.get(id=stop_id)
            stop.stop_number = index
            stop.eta = None
            stop.save()
            all_stops.append(stop)
    return render(request, 'partials/route_stop_list.html', {'all_stops': all_stops})

class ScheduleStopDetailView(AdminOrStaff):
    def get(self, request, pk):
        stop = ScheduleStop.objects.get(id=pk)
        form = ScheduleStopForm(
            initial={
                'customer': stop.customer,
                'stop_number': stop.stop_number,
                'status': stop.status,
                'eta': stop.eta,
                'start_time': stop.start_time,
                'end_time': stop.end_time,
                'note': stop.note,
                'expected_bags': stop.expected_bags,
                'expected_packages': stop.expected_packages,
                'expected_palets': stop.expected_palets,
                'received_palets': stop.received_palets,
                'received_bags': stop.received_bags,
                'received_packages': stop.received_packages,
                'image': stop.image,
                }
            )
        return render(request, 'schedule_stop_detail.html', {'form': form, 'stop': stop, 'id': pk})
    
    def post(self, request, pk):
        stop = get_object_or_404(ScheduleStop, pk=pk)
        form = ScheduleStopForm(request.POST, request.FILES, instance=stop)
        if form.is_valid():
            customer = form.cleaned_data['customer']
            # stop_number = form.cleaned_data['stop_number']
            stop.status = form.cleaned_data['status']
            stop.eta = form.cleaned_data['eta']
            stop.start_time =  form.cleaned_data['start_time']
            stop.end_time = form.cleaned_data['end_time']
            stop.note = form.cleaned_data['note']
            stop.expected_bags = form.cleaned_data['expected_bags']
            stop.expected_packages = form.cleaned_data['expected_packages']
            stop.expected_palets = form.cleaned_data['expected_palets']
            stop.received_palets = form.cleaned_data['received_palets']
            stop.received_bags = form.cleaned_data['received_bags']
            stop.received_packages = form.cleaned_data['received_packages']
            
            if form.cleaned_data['image'] !=None and form.cleaned_data['image'] !=False:
                image = form.cleaned_data['image']
            else:
                image = None
            stop.save()
            messages.success(request, 'Stop was updated successfully!', extra_tags='alert')
            return redirect('schedule_detail', stop.schedule_id)
        return render(request, 'schedule_stop_detail.html', {'form': form, 'id': pk, 'stop': stop})
    
    
@login_required()     
def delete_schedule_stop(request, pk):
    schedule_stop = get_object_or_404(ScheduleStop, pk=pk)
    schedule_id = schedule_stop.schedule_id
    schedule_stop.delete()
    existing_stops = ScheduleStop.objects.filter(schedule_id=schedule_id).order_by('stop_number')
  
    if not existing_stops.exists():
        messages.success(request, 'stop Successfully deleted', extra_tags='alert')
        return redirect('schedule_detail', schedule_id)
    # reorder the stop_number field
    with transaction.atomic():
        for index, stop in enumerate(existing_stops, start=1):
            stop.stop_number = index
            stop.save()
    messages.success(request, 'stop Successfully deleted', extra_tags='alert')
    return redirect('schedule_detail', schedule_id)

@login_required()
def delete_route_stop(request, pk):
    route_stop = get_object_or_404(RouteStop, pk=pk)    
    route_id = route_stop.route_id
    route_stop.delete()
    existing_stops = RouteStop.objects.filter(route_id=route_id).order_by('stop_number')
    
    if not existing_stops.exists():
        messages.success(request, 'stop Successfully deleted', extra_tags='alert')
        return redirect('route_detail', route_id)
    with transaction.atomic():
        for index, stop in enumerate(existing_stops, start=1):
            stop.stop_number = index
            stop.save()
    messages.success(request, 'stop Successfully deleted', extra_tags='alert')
    return redirect('route_detail', route_id)
    
    
    
    
class RouteListView(AdminOrStaff):
    def get(self, request):
        routs = Route.objects.all()
        return render(request, 'routs_list.html', {'routs':routs})
    
class RouteDetailView(AdminOrStaff):
    def get(self, request, pk):
        all_stops = RouteStop.objects.filter(route_id=pk).order_by('stop_number')
        total_stops_count = range(1, all_stops.count() + 1)
        route = get_object_or_404(Route, pk=pk)
        return render(request, 'route_detail.html',
                {
                'route': route,
                'all_stops': all_stops,
                'id': pk,
                'total_stops_count':total_stops_count
                }
            )
    
    def post(self, request, pk):
        breakpoint()
        stops = dict(request.POST)
        csfrtoken, *stop_ids = stops
        with transaction.atomic():
            #loop over all stop id's from the form
            all_stops = RouteStop.objects.filter(route=pk)
            for stop_id in stop_ids:
                # select a given stop by its id
                stop = all_stops.select_for_update().get(id=int(stop_id))
                # update the stops stop_number with the forms new input value
                stop.stop_number = int(stops[stop_id][0])
                stop.save()
        messages.success(request, 'Stop order Successfully Changed', extra_tags='alert')
        all_stops = RouteStop.objects.all()
        total_stops_count = range(1, all_stops.count() + 1)
        route = get_object_or_404(Route, pk=pk)
        return render(request, 'route_detail.html',
                {
                'route': route,
                'all_stops': all_stops,
                'id': pk,
                'total_stops_count':total_stops_count
                }
        )
    
class CreateRouteView(AdminOrStaff):
    def get(self, request):
        form = CreateRouteForm()
        return render(request, 'create_route.html', {'form': form})
    
    def post(self, request):
        form = CreateRouteForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            Route.objects.create(name=name)
            messages.success(request, 'stop Successfully Created', extra_tags='alert')
            return redirect('routs')
        return render(request, 'create_route.html', {'form': form})

@login_required() 
def delete_route(request, pk):
    rout_stop = get_object_or_404(Route, pk=pk)
    rout_stop.delete()
    messages.success(request, 'Stop Successfully deleted', extra_tags='alert')
    return redirect('routs')



class CreateRouteStopView(AdminOrStaff):
    def get(self, request, pk):
        form = CreateRouteStopForm()
        return render(request, 'create_route_stop.html', {'form': form})
    
    def post(self, request, pk):
        form = CreateRouteStopForm(request.POST)
        if form.is_valid():
            route = get_object_or_404(Route, pk=pk)
            stops = route.routestop_set
            # if this is the first stop in the list 
            if stops.first() == None:
                stop_number = 1
            # if there are already stops in this route get the last stop_number and add 1
            else:
                stops_ordered = stops.order_by('stop_number')
                last_stop_number = stops_ordered.last().stop_number
                stop_number = last_stop_number+1
            
            customer = form.cleaned_data['customer']
            general_note = form.cleaned_data['general_note']
            RouteStop.objects.create(route=route,
                                     customer=customer,
                                     stop_number=stop_number,
                                     general_note=general_note
                                     )
            messages.success(request, 'stop Successfully Created', extra_tags='alert')
            return redirect('route_detail', pk)
        return render(request, 'create_route.html', {'form': form})
            

class RouteStopDetailView(AdminOrStaff):
    def get(self ,request, pk):
        stop = get_object_or_404(RouteStop, pk=pk)
       
        # this form is used here as a update form
        form = CreateRouteStopForm(
            initial={'customer':stop.customer,
                     'general_note':stop.general_note
                     }) 
        return render(request, 'route_stop_detail.html', {'form': form, 'pk': pk})

    def post(self, request, pk):
        stop = get_object_or_404(RouteStop, pk=pk)
        form = CreateRouteStopForm(request.POST)
        if form.is_valid():
            # if the user has changed we need to remove the eta from that stop as well
            if stop.customer != form.cleaned_data['customer']:
                stops = RouteStop.objects.filter(route_id=stop.route_id)
                for stop in stops:
                    stop.eta = None
                    stop.save()
            stop.customer = form.cleaned_data['customer']
            stop.general_note = form.cleaned_data['general_note']
            stop.save()
            messages.success(request, 'Stop Updated Successfully', extra_tags='alert')
            return redirect('route_detail', stop.route_id)
        messages.error(request, 'Error Updating Stop Info', extra_tags='alert')
        return render(request, 'route_stop_detail.html', {'form': form, 'pk': pk})
        
@login_required()
def add_etas_to_route_stops(request, pk):
    # create time instance to pass to the google api
    today = datetime.date.today()
    threePm = datetime.time(hour=15)
    today_three_pm = datetime.datetime.combine(today, threePm)
    # get stops to calculate eta
    all_stops = RouteStop.objects.filter(route_id=pk).order_by('stop_number')

    all_etas = {}
    errors = []
    departure_time = datetime.datetime.now() # for now till we figure oure the sintex of creating a datetime object with a specific time
    with ThreadPoolExecutor(max_workers=10) as executor:
            for stop_number, stop in enumerate(all_stops):
                executor.submit(fetch_stop_etas_for_routes, all_stops, stop_number,  all_etas, departure_time, errors)
     
    if len(errors) > 0:
        messages.error(request, f'{errors[0]}', extra_tags='alert')
    else:
        # loop over the all_etas and make add the prev stops time to the eta of a later stop
        for i in range(1, len(all_etas) + 1):
            if i > 2:
                all_etas[i] = (all_etas[i-1] + all_etas[i]) 
        # we updated the data base with the new eta's for every stop
        for stop in all_stops:
            stop_object = RouteStop.objects.get(id=stop.id)
            stop_object.eta = all_etas[stop_object.stop_number]
            stop_object.save()    
        # relay we should have a success message only the way it is set up now the message fragment is in the base template which is not rerendered to display the message    
        # messages.success(request, 'Successfully Updated Etas for route stops', extra_tags='alert')
        
    all_stops = RouteStop.objects.filter(route_id=pk).order_by('stop_number')
    return render(request, 'partials/route_stop_list.html', {'all_stops': all_stops})
    
##############   DRIVER APP   ################
class DriversHomeView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'driver_landing_page.html')
    
    
class StopsView(LoginRequiredMixin, ListView):
    def get(self, request):
        # get all stops for

        schedule = Schedule.objects.filter(
            driver__id=request.user.id,
            start_time__date=datetime.date.today()
            ).first()
       
        if schedule: # if there is a schedule with a start_time within 24 hours.. we will look for its stops
            schedule_stops = schedule.schedulestop_set.all().order_by('stop_number')
            stops_count = schedule_stops.count()
            stops_completed = schedule_stops.filter(status='CP').count()
        else:
            return render(request, 'stops.html', {'stops': 0})
        paginator = Paginator(schedule_stops, 1)
        page_number = request.GET.get('page', 1)
        try:
            stops = paginator.page(page_number)
            form = FeedbackFrom(initial={
                'feedback_note': stops[0].feedback_note,
                'received_bags': stops[0].received_bags,
                'received_palets': stops[0].received_palets,
                'heavy_bag': stops[0].heavy_bag,
                'no_papers': stops[0].no_papers,
                'no_bags': stops[0].no_bags,
                'image': stops[0].image,
                })
        except EmptyPage:
            stops = paginator.page(paginator.num_pages)

        palets_options = ScheduleStop.PALETS_PAYLOAD
        bags_options = ScheduleStop.BAGS_PAYLOAD
        return render(request,
                      'stops.html',
                      {'stops': stops,
                       'form': form,
                       'stops_count': stops_count,
                       'stops_completed': stops_completed,
                       'palets_options':palets_options,
                       'bags_options':bags_options,
                       'schedule_id': schedule.id,
                       }
                      )
        
    def post(self, request):
        # GET THE HIDDEN INPUT VALUE TO GET THE ID OF THE STOP
        # AND FINISH UP WITH THIS VIEW
        form = FeedbackFrom(request.POST, request.FILES)
        stop_id = int(request.POST.get('stop_id'))
        schedulestop = get_object_or_404(ScheduleStop, pk=stop_id)
        if form.is_valid():
            schedulestop.feedback_note = form.cleaned_data['feedback_note']
            schedulestop.received_bags = form.cleaned_data['received_bags']
            schedulestop.received_palets = form.cleaned_data['received_palets']
            schedulestop.heavy_bag = form.cleaned_data['heavy_bag']
            schedulestop.no_papers = form.cleaned_data['no_papers']
            schedulestop.no_bags = form.cleaned_data['no_bags']
            if form.cleaned_data['image'] != None and form.cleaned_data['image'] !=False:
                  schedulestop.image = form.cleaned_data['image']
            else:
                schedulestop.image = None
            schedulestop.status = 'CP'
            schedulestop.save()
            
            # now we need to see if all the stops have been completed if it has we want to to mark the schedule as FN if not we want to mark it as IP for in progress
            ###### GET STOP'S / PAGINATED STOPs
            schedule = Schedule.objects.filter(
                driver__id=request.user.id,
                start_time__date=datetime.date.today()
                )
            
            ##### UPDATE PARENT SCHEDULE STATUS #####
            if schedule: # if there is a schedule with a start_time within 24 hours.. we will look for its stops
                schedule_stops = schedule.first().schedulestop_set.all().order_by('stop_number')
                # update the schedule status based on the amount of stops completed
                stops_count = schedule_stops.count()
                stops_completed = schedule_stops.filter(status='CP').count()
                parent_schedule = Schedule.objects.get(id=schedule_stops.first().schedule.id)
                if stops_count > stops_completed & stops_completed != 0:
                    if parent_schedule.status == 'NS': # if it is not yet marked as started do so 
                        parent_schedule.status = 'IP'
                        parent_schedule.save()
                if stops_count == stops_completed:
                    parent_schedule.status = 'FN'
                    parent_schedule.save()
            else:
                schedule_stops = schedule
            paginator = Paginator(schedule_stops, 1)
            page_number = request.GET.get('page', 1)
            try:
                stops = paginator.page(page_number)
            except EmptyPage:
                stops = paginator.page(paginator.num_pages)
       
            messages.success(request, 'Successfully Submitted Feedback', extra_tags='alert')
            return render(request, 'stops.html', {'form': form,
                                                  'stops': stops,
                                                  'stops_count': stops_count,
                                                  'stops_completed': stops_completed,
                                                  })
            
            
class DriverFeedBackView(View):
    def get(self, request, pk):
        form = FeedbackFrom()
        return render(request, 'feed_back_form.html', {'form':form, 'stop_id': pk})

    
class DriverProfileView(View):
    def get(self, request):
        form = DriverProfileForm(initial={
                    'username': request.user.username,
                    'phone_number': request.user.phone_number
                })
        return render(request,
                      'driver_profile.html',
                      {'form': form})
    
    def post(self, request):
        form = DriverProfileForm(request.POST)
        user = get_object_or_404(CustomUser, id=request.user.id)

        if form.is_valid():
            user.username = form.cleaned_data['username']
            user.phone_number = form.cleaned_data['phone_number']
            user.save()
            messages.success(request, 'Successfully Updated Profile', extra_tags='alert')
        return render(request, 'driver_profile.html', {'form': form})
    
@login_required() 
def update_drivers_location(request, latitude, longitude, schedule_id):
    now = timezone.now()
    driver = get_object_or_404(CustomUser, id=request.user.id)
    driver.latitude = latitude
    driver.longitude = longitude
    driver.position_timestamp = now
   
    driver.save()
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    schedule.last_eta_update_timestamp = now
    schedule.save()
  
    return HttpResponse('202', content_type='text/plain') 

@login_required()
def notify_of_driver_location_error(request):
    driver = request.user
    response = send_gps_error_message(driver)
    return HttpResponse(status='202') 