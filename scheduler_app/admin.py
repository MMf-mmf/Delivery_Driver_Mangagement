from django.contrib import admin
from .models import Vehicle, Schedule, ScheduleStop, Route, RouteStop

class VehicleAdmin(admin.ModelAdmin):
        model = Vehicle
        list_display = [
                "name",
                "make",
                "lift_gate",
                ]
    
class ScheduleAdmin(admin.ModelAdmin):
    model = Schedule
    list_display = [
        "driver",
        "start_time",
        "status"
    ]
    
class ScheduleStopAdmin(admin.ModelAdmin):
    model = ScheduleStop
    list_display = [
        "schedule",
        "customer",
        "status"
    ]
    
class RouteAdmin(admin.ModelAdmin):
    model = Route
    list_display = [
        "name"
    ]

class RouteStopsAdmin(admin.ModelAdmin):
    model = RouteStop
    list_display = [
        "customer",
        "route_id"
    ]
    
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(ScheduleStop, ScheduleStopAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(RouteStop, RouteStopsAdmin)
