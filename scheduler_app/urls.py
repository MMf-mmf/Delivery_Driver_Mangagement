from django.urls import path, re_path
from .views import (
    CreateVehicleView,VehicleListView,
    VehicleDetailView, delete_vehicle,
    CreateScheduleView, CreateRouteView,
    ScheduleListView, ScheduleDetailView,
    ScheduleStopDetailView, delete_schedule_stop,
    delete_schedule, RouteListView,RouteDetailView,
    delete_route, delete_route_stop, CreateRouteStopView,
    RouteStopDetailView, StopsView, DriverProfileView,
    AddScheduleStopView, DriverFeedBackView,
    DriversHomeView, sort_schedule_stop, sort_route_stop,
    update_drivers_location, DriverScheduleLocation,
    add_etas_to_route_stops, updateScheduleStopEtas,
    notify_of_driver_location_error,
    )


vehicle = [
    path('create_vehicle/', CreateVehicleView.as_view(), name='create_vehicle'),
    path('vehicle_list/', VehicleListView.as_view(), name='vehicles'),
    path('vehicle/<int:pk>/', VehicleDetailView.as_view(), name='vehicle_detail'),
    path('vehicle/<int:pk>/delete', delete_vehicle, name='delete_vehicle'),
]

schedule = [
    path('create_schedule/', CreateScheduleView.as_view(), name='create_schedule'),
    path('schedule_list/', ScheduleListView.as_view(), name='schedules'),
    path('schedule/<int:pk>/', ScheduleDetailView.as_view(), name='schedule_detail'),
    path('schedule/<int:pk>/delete/', delete_schedule, name='delete_schedule'),
    path('schedule/<int:pk>/add/', AddScheduleStopView.as_view(), name='add_schedule_stop'),
    path('schedule_stop/<int:pk>/', ScheduleStopDetailView.as_view(), name="schedule_stop_detail"),
    path('schedule_stop/<int:pk>/delete/', delete_schedule_stop, name='delete_schedule_stop'),
    path('sort_schedule_stop/<int:pk>/', sort_schedule_stop, name='sort_schedule_stop'),
    path('current_drivers_location_on_schedule/<int:pk>/', DriverScheduleLocation.as_view(), name='driver_location_on_schedule'),
    path('update_schedule_stop_etas/<int:pk>/', updateScheduleStopEtas, name='update_schedule_stops_etas')
]

route = [
    path('create_route/', CreateRouteView.as_view(), name='create_route'),
    path('routs/', RouteListView.as_view(), name='routs'),
    path('routs/<int:pk>/', RouteDetailView.as_view(), name='route_detail'),
    path('sort_route_stop/', sort_route_stop, name='sort_route_stop'),
    path('route/<int:pk>/delete/', delete_route, name='delete_route'),
    path('route/<int:pk>/create_stop/', CreateRouteStopView.as_view(), name='create_route_stop'),
    path('route/stop/<int:pk>/', RouteStopDetailView.as_view(), name='route_stop_detail'),
    path('route_stop/<int:pk>/delete/', delete_route_stop, name='delete_route_stop'),
    path('add_etas_to_route_stops/<int:pk>/', add_etas_to_route_stops, name='add_etas_to_route_stops')
]

driver = [
    path('drivers_home/', DriversHomeView.as_view(), name='drivers_home'),
    path('stops/', StopsView.as_view(), name='stops'),
    path('driver_profile/', DriverProfileView.as_view(), name='driver_profile'),
    path('driver_feedback/<int:pk>/', DriverFeedBackView.as_view(), name='driver_feedback'),
    path('update_drivers_location/<str:latitude>/<str:longitude>/<int:schedule_id>/', update_drivers_location, name='update_drivers_location'),
    path('drivers_location_error/', notify_of_driver_location_error, name='drivers_location_error')
]

urlpatterns = [
   *vehicle,
   *schedule,
   *route,
   *driver,
]

# re_path(r'^update_drivers_location/(?P<latitude>(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?)))/(?P<longitude>(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?)))/$', update_drivers_location, name='update_drivers_location'),
