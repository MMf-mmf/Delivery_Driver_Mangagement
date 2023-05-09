from django.urls import path
from .views import DriverListView, DriverDetailView, CustomerListView, CustomerDetailView, CreateDriver, DeleteUserView, CreateCustomer

"""as of now for safety we don't plan on having a sign up form all adding of users should be done throw the admin"""
urlpatterns = [
     path("customers/", CustomerListView.as_view(), name="customers"),
     path("customer/<int:pk>/", CustomerDetailView.as_view(), name="customer_detail"),
     path('drivers/', DriverListView.as_view(), name="drivers"),
     path("driver/<int:pk>/", DriverDetailView.as_view(), name="driver_detail"),
     path("create_driver/", CreateDriver.as_view(), name="create_driver"),
     path("delete_user/<int:pk>/", DeleteUserView.as_view(), name='delete_user'),
     path("create_customer/", CreateCustomer.as_view(), name="create_customer"),
]
 