from django.db import models
from accounts_app.models import CustomUser
from utils.abstract_model import TimeStampedModel
import uuid 

class Vehicle(TimeStampedModel):
    name = models.CharField(max_length=30, null=False, blank=False)
    make = models.CharField(max_length=30, null=False, blank=False)
    model = models.CharField(max_length=30, null=False, blank=False)
    year = models.CharField(max_length=10, null=False, blank=False)
    image = models.ImageField(upload_to='vehicles', blank=True, null=True)
    capacity = models.CharField(max_length=10, null=True, blank=True)
    lift_gate = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
# Default Route    
class Route(TimeStampedModel):
    name = models.CharField(max_length=30, null=False, blank=False, unique=True)
    durations = models.CharField(max_length=350, null=True, blank=True)
    def __str__(self):
        return f"{self.id} {self.name}"
    
# Default Route
class RouteStop(TimeStampedModel):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    stop_number = models.PositiveIntegerField(null=False, blank=False)
    eta = models.CharField(max_length=10,null=True, blank=True)
    general_note = models.CharField(max_length=50, null=True, blank=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['stop_number', 'route'], name='unique_stop_number', deferrable=models.Deferrable.DEFERRED),
            # models.UniqueConstraint(fields=['customer', 'route'], name='no_duplicate_customers_in_route')
        ]

    def __str__(self):
        return f"{self.route} Customer: {self.customer}"
    
class Schedule(TimeStampedModel):
    # CHOICE OPTIONS
    NOT_STARTED = 'NS'
    IN_PROGRESS = 'IP'
    FINISHED = 'FN'
    SCHEDULE_STATUS = [
        (NOT_STARTED, 'Not Started'),
        (IN_PROGRESS, 'In Progress'),
        (FINISHED, 'Finished'),
    ]
    PALETS_PAYLOAD = [tuple([x,x]) for x in range(0,13)]
    BAGS_PAYLOAD = [tuple([x,x]) for x in range(0,21)]

    # FIELDS
    # WE MUST WIPE THE DATA BASE FIRST BEFORE CHANGING THE IDS TO UUIDS
    # id = models.UUIDField(  
    #     primary_key=True,
    #     default=uuid.uuid4,
    #     editable=False)
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='driver_schedule')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='vehicle')
    route_name = models.CharField(max_length=50, blank=False)
    start_time = models.DateTimeField(null=False)
    status = models.CharField(max_length=2, choices=SCHEDULE_STATUS, default=NOT_STARTED)
    total_palets = models.DecimalField(max_digits=2, choices=PALETS_PAYLOAD, default=0, decimal_places=0)
    total_bags = models.DecimalField(max_digits=5, choices=BAGS_PAYLOAD, default=0, decimal_places=0)
    total_packages = models.DecimalField(max_digits=5, decimal_places=0, default=0)
    image = models.ImageField(upload_to='schedule', blank=True, null=True)
    # every time a eta of a  stop in this schedule is updated this felid is updated to that time 
    last_eta_update_timestamp = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"driver name: {self.driver} Date {self.start_time} "
    
class ScheduleStop(TimeStampedModel):
    
    STATUS = [
        ('IC', 'incomplete'),
        ('CP', 'complete'),
    ]
    
    PALETS_PAYLOAD = [tuple([x,x]) for x in range(0,11)]
    BAGS_PAYLOAD = [tuple([x,x]) for x in range(0,21)]
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    stop_number = models.PositiveIntegerField(null=False, blank=False)
    status = models.CharField(max_length=2,  choices=STATUS, default='IC')
    eta = models.PositiveIntegerField(null=True, blank=True) # value in seconds
    start_time = models.DateTimeField(auto_now=False,auto_now_add=False, null=True, blank=True)
    end_time = models.DateTimeField(auto_now=False,auto_now_add=False, null=True, blank=True)
    note = models.CharField(max_length=250, blank=True, null=True)
    
    expected_palets = models.DecimalField(max_digits=5, decimal_places=0, default=0)
    expected_bags =  models.DecimalField(max_digits=5, decimal_places=0, default=0)
    expected_packages =  models.DecimalField(max_digits=5, decimal_places=0, default=0)
    '''driver inputs feedback'''
    feedback_note = models.CharField(max_length=250, blank=True, null=True)
    received_packages =  models.DecimalField(max_digits=5, decimal_places=0, default=0)
    received_palets = models.DecimalField(max_digits=5, decimal_places=0, default=0, choices=PALETS_PAYLOAD)
    received_bags =  models.DecimalField(max_digits=5, decimal_places=0, default=0, choices=BAGS_PAYLOAD)
    heavy_bag = models.BooleanField(default=False) # 45lb+
    no_papers = models.BooleanField(default=False)
    no_bags = models.BooleanField(default=False)
    image = models.ImageField(upload_to='stop', blank=True, null=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['schedule', 'stop_number'],
                name='unique_stop_per_schedule',
                deferrable=models.Deferrable.DEFERRED
                ),
        ]
        
    
    def __str__(self):
        return f"{self.schedule} Customer: {self.customer} "