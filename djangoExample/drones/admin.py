from django.contrib import admin
from drones.models import Drone, DroneCategory, Pilot, Competition

# Register your models here.
admin.site.register(Drone)
admin.site.register(DroneCategory)
admin.site.register(Pilot)
admin.site.register(Competition)