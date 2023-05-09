from django.db import models

from django.contrib.auth.models import AbstractUser, BaseUserManager, UserManager
from django.urls import reverse


class StaffManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_staff=True)
class DriverManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_driver=True)
class CustomerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_customer=True)
class CustomUserManger(UserManager):
  pass
# https://docs.djangoproject.com/en/2.0/ref/contrib/auth/#fields
class CustomUser(AbstractUser):
    name = models.CharField(null=True, blank=True, max_length=100)
    phone_number = models.CharField(null=True, blank=True, max_length=25)
    is_driver = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    # Note! "is_staff" is already in the the AbstractUser
    business_name = models.CharField(null=True, blank=True, max_length=100)
    address = models.CharField(null=True, blank=True, max_length=200)
    contact_name = models.CharField(null=True, blank=True, max_length=100)
    contact_number = models.CharField(null=True, blank=True, max_length=50)
    latitude = models.CharField(null=True, blank=True, max_length=50)
    longitude = models.CharField(null=True, blank=True, max_length=50)
    position_timestamp = models.DateTimeField(null=True, blank=True)
    comments = models.CharField(null=True, blank=True, max_length=350)
    # model managers
    objects = CustomUserManger()
    staff_objects = StaffManager()
    driver_objects = DriverManager()
    customer_objects = CustomerManager()
    
    
    # def get_absolute_url(self):
    #     """Returns the URL to access a detail record for this book."""
    #     return reverse('customer-detail', args=[str(self.id)])
                        
    
