import json
import googlemaps
from django.conf import settings


""" use google distance api to calculate the distance between tow stops and in our case repeat this"""

# this function should return a takes in a empty object and return a object with the keys the stop number and the values the eta in seconds
def fetch_stop_etas(all_stops, stop_number, drivers_lat, drivers_lon, all_etas, departure_time, errors):
    biz_lat = all_stops[stop_number].customer.latitude
    biz_lon = all_stops[stop_number].customer.longitude
    gmaps = googlemaps.Client(key= settings.GOOGLE_API_KEY)
 
    # if stop number is 0 or prev stop is completed get starting location from driver
    
    if (stop_number == 0 ):
        try:
            result = gmaps.distance_matrix(f'{drivers_lat} {drivers_lon}',f"{biz_lat} {biz_lon}",mode="driving", units="imperial", departure_time=departure_time)
        except Exception as e:
            errors.append(f'A Error accrued while getting the stops eta from google Please contact IT. error:{e}')
    
    elif (all_stops[stop_number - 1].status == 'CP'):
        result = gmaps.distance_matrix(f'{drivers_lat} {drivers_lon}',f"{biz_lat} {biz_lon}",mode="driving", units="imperial", departure_time=departure_time)
    else:
        prev_biz_lat = all_stops[stop_number - 1].customer.latitude
        prev_biz_lon = all_stops[stop_number - 1].customer.longitude
        try:
            result = gmaps.distance_matrix(f'{prev_biz_lat} {prev_biz_lon}',f"{biz_lat} {biz_lon}",mode="driving", units="imperial", departure_time=departure_time)
        except Exception as e:
            errors.append(f'A Error accrued while getting the stops eta from google Please contact IT. error:{e}')
            
    clean_data_1 = json.dumps(result)
    clean_data_2 = json.loads(clean_data_1)
    duration = clean_data_2['rows'][0]['elements'][0]['duration']['value']
    
    all_etas[stop_number + 1] = duration


   
def fetch_stop_etas_for_routes(all_stops, stop_number, all_etas, departure_time, errors):
    biz_lat = all_stops[stop_number].customer.latitude
    biz_lon = all_stops[stop_number].customer.longitude
    gmaps = googlemaps.Client(key= settings.GOOGLE_API_KEY)
 

    # if stop number is 0 we don't as of now have a starting place to sto we are going to leave it blank
    if (stop_number == 0 ):
        all_etas[stop_number + 1] = None
    else:
        prev_biz_lat = all_stops[stop_number - 1].customer.latitude
        prev_biz_lon = all_stops[stop_number - 1].customer.longitude
        try: 
            result = gmaps.distance_matrix(f'{prev_biz_lat} {prev_biz_lon}',f"{biz_lat} {biz_lon}",mode="driving", units="imperial", departure_time=departure_time)
        except Exception as e:
            errors.append(f'A Error accrued while getting the stops eta from google Please contact IT. error:{e}')
        clean_data_1 = json.dumps(result)
        clean_data_2 = json.loads(clean_data_1)
        duration = clean_data_2['rows'][0]['elements'][0]['duration']['value']
        
        all_etas[stop_number + 1] = duration