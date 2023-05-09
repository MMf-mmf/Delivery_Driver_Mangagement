from django import template
from ..models import Schedule
from django.db.models import Sum

register = template.Library()
# simple tag to return the amount of completed schedules
@register.simple_tag
def total_schedules():
    return Schedule.objects.filter(status="FN").count()

# inclusion tag to receive driver id and return data about that drivers stats
@register.inclusion_tag('inclusion_driver_stats.html')
def driver_stats(driverId):
    (
    stop_info_summery := Schedule.objects.filter(driver_id=driverId)
    .values('id', 'schedulestop__received_bags', 'schedulestop__received_palets')
    .aggregate(bags=Sum('schedulestop__received_bags'), palets=Sum('schedulestop__received_palets'))
    )
    total_schedules = Schedule.objects.filter(driver_id=driverId, status="FN").count()
    return {'total_bags': stop_info_summery['bags'], 'total_palets': stop_info_summery['palets'], 'total_schedules': total_schedules}
# this tag douse douse mostly the same thing as driver_stats - the template to use this tag the html will need to be clearly written out this can be beneficial when the html needs to be different


@register.simple_tag
def driver_data_summery(driverId):
    (
    stop_info_summery := Schedule.objects.filter(driver_id=driverId)
    .values('id', 'schedulestop__received_bags', 'schedulestop__received_palets')
    .aggregate(bags=Sum('schedulestop__received_bags'), palets=Sum('schedulestop__received_palets'))
    )
    total_schedules = Schedule.objects.filter(driver_id=driverId, status="FN").count()
    return {'total_bags': stop_info_summery['bags'], 'total_palets': stop_info_summery['palets'], 'total_schedules': total_schedules}
