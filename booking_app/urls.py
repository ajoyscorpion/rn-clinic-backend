from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home')
    path('doctors/',views.doctor_list,name='doctor_list'),
    path('view-doctor/<int:id>',views.view_doctor,name='view_doctor'),
    path('signup/',views.sign_up,name='sign_up'),
    path('signin/',views.sign_in,name="sign_in"),
    path('handlemeet/',views.handle_meet,name="handle_meet"),
    path('mybookings/',views.my_bookings,name='my_bookings'),
    path('cancelBooking/',views.cancel_booking,name='cancel_booking'),
    path('updateDateTime/',views.update_date_time,name='update_date_time'),
    path('bookedDatesTimes',views.booked_dates_times,name='booked_dates_times'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('userdetails/<str:user_id>/',views.getUserDetails,name='get_user_details'),
    path('sendEmail/',views.send_email,name="send_email")
]