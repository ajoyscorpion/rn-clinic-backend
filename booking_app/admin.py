from django.contrib import admin
from .models import Appointment, Doctors,CustomUser
#from django.contrib.auth import get_user_model
# # Register your models here.


admin.site.register(Doctors)

#admin.site.register(get_user_model())
admin.site.register(CustomUser)

admin.site.register(Appointment)

