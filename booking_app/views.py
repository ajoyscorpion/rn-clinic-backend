from django.shortcuts import render
from django.http import JsonResponse
from .models import CustomUser, Doctors, Appointment, UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
#from django.middleware.csrf import get_token
import json
from django.utils.dateparse import parse_date, parse_time
from django.core.exceptions import ObjectDoesNotExist
import traceback
from datetime import datetime
import os
import resend
from django.http import HttpResponse


def home(request):
    return HttpResponse("RN Clinic - Doctor Booking App Server ")


def doctor_list(request):
    doctors = Doctors.objects.all().values()

    print(f"Number of doctors: {len(doctors)}")

    return JsonResponse(list(doctors),safe=False)



def view_doctor(request,id):
    try:
        doctor = Doctors.objects.get(pk=id)
        doctor_data = {
            'id':doctor.id,
            'name':doctor.name,
            'department' : doctor.department,
            'img' : doctor.img.url,
            'rating':doctor.rating
        }

        return JsonResponse(doctor_data)

    except Doctors.DoesNotExist:
        return JsonResponse({'error':'Doctor not found'},status=404)


@csrf_exempt
def sign_up(request):
    
    if request.method == 'POST':

        data = json.loads(request.body)

        name = data.get('name')
        email = data.get('email')
        password = data.get('pswd')
        phone = data.get('phone')

        try:
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'},status = 400)

            user = CustomUser.objects.create_user(email=email,name=name,password=password,phone=phone)

            serialized_user = {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'address': user.address,
                'phone': user.phone
            }

            print("The registered user : ",serialized_user)
            return JsonResponse({'success': 'User created successfully' ,'user': serialized_user}, status=201)
        
        except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def sign_in(request):
    if request.method == 'POST':
        try:
            # Load JSON data from the request body
            data = json.loads(request.body)

            email = data.get('email')
            password = data.get('pswd')

            # Authenticate the user
            user = authenticate(request, email=email, password=password)

            if user is not None:
                
                customer_id = user.customer_id

                serialized_user = {
                'email': user.email,
                'name': user.name,
                'customer_id':customer_id
                }

                login(request, user)
                # Return success response

                print("The signed in user : ",serialized_user)
                return JsonResponse({'success': 'Sign-in successful', "user":serialized_user})
            else:
                # Invalid credentials
                return JsonResponse({'error': 'Invalid email or password'}, status=400)
        
        except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def handle_meet(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)

            doctor_id = data.get('doctor_id')
            user_id = data.get('user_id')
            date_of_appointment_str = data.get('date_of_appointment')
            time_of_appointment_str = data.get('time_of_appointment')
            online = data.get('online')
            offline = data.get('offline')
            booking_status = data.get('booking_status')

            doctor = Doctors.objects.get(pk=doctor_id)
            user = CustomUser.objects.get(customer_id = user_id)

            print(doctor.id)
            print(user.customer_id)

            date_of_appointment = parse_date(date_of_appointment_str)
            time_of_appointment = parse_time(time_of_appointment_str)
            
            print(date_of_appointment)
            print(time_of_appointment)

            appointment = Appointment.objects.create(
                user=user,
                doctor=doctor,
                date_of_appointment=date_of_appointment,
                time_of_appointment=time_of_appointment,
                offline=offline,
                online=online,
                booking_status=booking_status,
            )

            print(appointment)

            appointment_data = {
                'booking_id': appointment.booking_id,
                'user_id': appointment.user.customer_id,
                'user_name': appointment.user.name,
                'doctor_id': appointment.doctor.id,
                'doctor_name': appointment.doctor.name,
                'date_of_appointment': appointment.date_of_appointment,
                'time_of_appointment': appointment.time_of_appointment,
                'offline': appointment.offline,
                'online': appointment.online,
                'virtual_link': appointment.virtual_link,
                'booking_status': appointment.booking_status
            }

            print(appointment_data)

            # Process the meeting request here
            return JsonResponse({'success': 'Susccesfully registered', 'data': appointment_data},status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)



@csrf_exempt
def my_bookings(request):
    #if request.method == 'POST':
        try:
            data = json.loads(request.body)

            user_id = data.get('user_id')
            print(data)
            print(user_id)

            customerId = CustomUser.objects.get(customer_id = user_id)
            print(customerId.id)    

            myBooking = Appointment.objects.filter(user_id = customerId.id)

            print(myBooking)

            bookings_data = [{
                'booking_id':booking.booking_id,
                'date_of_appointment':booking.date_of_appointment,
                'time_of_appointment':booking.time_of_appointment,
                'booking_status':booking.booking_status,
                'offline':booking.offline,
                'online':booking.online,
                'virtual_link':booking.virtual_link,
                'doctor_pic':booking.doctor.img.url,
                'doctor_name':booking.doctor.name
            }for booking in myBooking]

            print(bookings_data)

            return JsonResponse({'success': 'Successfully acheived', 'data':bookings_data},status=200)
        except:
            return JsonResponse({'error' : 'Invalid request method'},status=405)


@csrf_exempt
def cancel_booking(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            bookingId = data.get('booking_id')
            print(bookingId)

            booking = Appointment.objects.get(booking_id=bookingId)
            booking.booking_status = 'Cancelled'
            print(booking.booking_status)
            booking.save()

            booking_data = {
                'booking_id': booking.booking_id,
                'user': booking.user.id,
                'doctor': booking.doctor.id,
                'date_of_appointment': booking.date_of_appointment,
                'time_of_appointment': booking.time_of_appointment,
                'booking_status': booking.booking_status,
            }



            return JsonResponse({'Success':"Cancelled the Booking",'data':booking_data}, status = 200)
        except:
            return JsonResponse({'error':'Invalid request method'}, status = 405)



@csrf_exempt
def update_date_time(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            bookingId = data.get("booking_id")
            date_of_appointment_str = data.get('updatedDate')
            time_of_appointment_str = data.get('updatedTime')
            print(data)
            print(date_of_appointment_str)
            print(time_of_appointment_str)
            print("fuck")

            update_date_of_appointment = parse_date(date_of_appointment_str)
            update_time_of_appointment = parse_time(time_of_appointment_str)
            #print(update_date_of_appointment)
            #print(update_time_of_appointment)

            booking = Appointment.objects.get(booking_id=bookingId)
            print(booking)
            booking.date_of_appointment = update_date_of_appointment
            booking.time_of_appointment = update_time_of_appointment
            booking.save()

            booking_data = {
                'booking_id': booking.booking_id,
                'user': booking.user.id,
                'doctor': booking.doctor.id,
                'date_of_appointment': booking.date_of_appointment,
                'time_of_appointment': booking.time_of_appointment,
                'booking_status': booking.booking_status,
            }

            return JsonResponse({'Success':"Updated the Booking","data":booking_data}, status = 200)
        except:
            return JsonResponse({'error':'Invalid request method'}, status = 405)


def booked_dates_times(request):
    if request.method == 'GET':
        appointments = Appointment.objects.filter(booking_status="Booked")
        print(appointments)

        bookedDatesTimes = [
            {
                'date_of_appointment':appointment.date_of_appointment,
                'time_of_appointment':appointment.time_of_appointment
            }   
            for appointment in appointments
        ]
        print(bookedDatesTimes)

        return JsonResponse({'Booked_Dates_and_Time':bookedDatesTimes},status = 200)
    else:
        return JsonResponse({'error':'Invalid request method'},status=405)


@csrf_exempt
def update_profile(request):
    if request.method == 'POST':
        try:
            print("POST Data:", request.POST)
            print("FILES Data:", request.FILES)
            userId = request.POST.get("user_id")
            print(userId) 
            
            customer = CustomUser.objects.get(customer_id = userId)
            print(customer.id)


            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            address1 = request.POST.get('address1')
            address2 = request.POST.get('address2')
            city = request.POST.get('city')
            state = request.POST.get('state')
            pincode = request.POST.get('pincode')
            em_phone_no = request.POST.get('emPhoneNo')
            blood_Group = request.POST.get('bloodGroup')
            profile_image = request.FILES.get('profile_image')

            print("Hey")
            print(profile_image)

            try:
                user_profile = UserProfile.objects.get(user_id = customer.id)
                print(user_profile)
            except ObjectDoesNotExist:
                user_profile = UserProfile(user=customer)
            
            print("Hey Hey")

            user_profile.gender = gender
            if dob:
                try:
                    user_profile.dob = datetime.strptime(dob, '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({'error': 'Invalid date format. It must be in YYYY-MM-DD format.'}, status=400)
            else:
                user_profile.dob = None
            #user_profile.dob = dob
            user_profile.address1 = address1
            user_profile.address2 = address2
            user_profile.city = city
            user_profile.state = state
            user_profile.pincode = pincode
            user_profile.em_phone_no = em_phone_no
            user_profile.blood_group = blood_Group
            user_profile.profile_image = profile_image

            print(f"FILES: {request.FILES}")
            print(f"profileImage: {profile_image}")

            # if profile_image:
            #     print(f"Profile image name: {profile_image.name}")
            #     user_profile.profile_image.save(profile_image.name, profile_image)
            # else:
            #     print("No profile image uploaded")

            print("HEY HEY HEY")

            print(user_profile)

            user_profile.save()

            print(user_profile.profile_image) 
            
            print(gender)
            print(profile_image)
            return JsonResponse({'Success':"Updated the Profile"}, status = 200)
        except Exception as e:
            error_message = str(e)
            traceback.print_exc()
            return JsonResponse({'error':str(e)},status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)



@csrf_exempt
def getUserDetails(request,user_id):
    try:
        print(user_id)
        user = CustomUser.objects.get(customer_id = user_id)
        print(user)

        profile = UserProfile.objects.get(user_id = user.pk)
        print(profile)

        user_data = {
            "name":user.name,
            "email":user.email,
            "phone":user.phone,
            "customer_id":user.customer_id,
            "gender":profile.gender,
            "dob":profile.dob,
            "address1":profile.address1,
            "address2":profile.address2,
            "city":profile.city,
            "state":profile.state,
            "pincode":profile.pincode,
            "emPhoneNo":profile.em_phone_no,
            "bloodGroup":profile.blood_group,
            "profileImage":profile.profile_image.url if profile.profile_image else None
        }
        return JsonResponse({'success': 'Successfully acheived', 'data':user_data},status=200)
    except:
        return JsonResponse({'error' : 'Invalid request method'},status=405)


@csrf_exempt
def send_email(request):
    if request.method == "POST":
        
        data = json.loads(request.body)

        to = data.get('to')
        subject = data.get('subject')
        # html_content = request.POST.get('html_content')
        html_content = data.get("message")
        from_email = data.get("from","Acme <onboarding@resend.dev>")

        print(to)
        print("Hey")
        
        
        try:
            resend.api_key = os.getenv('RESEND_API_KEY')

            params = {
                "from": from_email,
                "to": [to],
                "subject": subject,
                "html": html_content,
            }

            email_response = resend.Emails.send(params)
            return JsonResponse({'status': 'success', 'data': email_response}, status=200)
        except Exception as e:
            error_message = str(e)
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


    return JsonResponse({'error': 'Invalid request method'}, status=400)