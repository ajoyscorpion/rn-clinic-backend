from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid
from django.core.validators import MaxValueValidator, MinValueValidator


# Doctor model
class Doctors(models.Model):
    name = models.CharField(max_length=100, unique=True)
    department = models.CharField(max_length=100)
    img = models.ImageField(upload_to='docImages')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])


class CustomUserManager(BaseUserManager):

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


# generate customer id
def generate_customer_id():
    prefix = "RNC"
    unique_id = str(uuid.uuid4()).replace('-','')
    return prefix + unique_id[:4]


# User Model
class CustomUser(AbstractUser):
    username = None
    customer_id = models.CharField(max_length=10, default=generate_customer_id, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100,unique=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=10,unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()

# generate booking id
def generate_booking_id():
    return str(uuid.uuid4())[:7]


# Appointment model
class Appointment(models.Model):
    booking_id = models.CharField(max_length=7, default=generate_booking_id, unique=True,null=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="appointment")
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE, related_name="appointment")
    date_of_appointment = models.DateField()
    time_of_appointment = models.TimeField()
    offline = models.BooleanField(default=False)
    online = models.BooleanField(default=False)
    virtual_link = models.URLField(max_length=200)
    booking_status = models.CharField(null=False, max_length=15)

    
    @property
    def customer_id(self):
        return self.customer.customer_id

    @property
    def customer_name(self):
        return self.customer.name

    @property
    def doctor_id(self):
        return self.doctor.id

    @property
    def doctor_name(self):
        return self.doctor.name


# user profile
class UserProfile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="userprofile")
    gender = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    address1 = models.CharField(max_length=200, blank=True, null=True)
    address2 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    em_phone_no = models.CharField(max_length=10, blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    profile_image = models.ImageField(upload_to="userImages", blank=True, null=True)








# from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# # Create your models here.

# class Doctors(models.Model):
#     name = models.CharField(max_length=100)
#     department = models.CharField(max_length=100)
#     img = models.ImageField(upload_to='docImages')


# class CustomUserManager(BaseUserManager):

#     def create_user(self,email,password=None, **extra_fields):
#         if not email:
#             raise ValueError("Email must be set")
#         email = self.normalize_email(email)
#         extra_fields.setdefault('is_staff', False)
#         extra_fields.setdefault('is_superuser', False)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         """Create and save a SuperUser with the given email and password."""
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')

#         return self._create_user(email, password, **extra_fields)



# class CustomUser(AbstractBaseUser):
#     username = None
#     email = models.EmailField(unique=True)
#     name = models.CharField(max_length=100)
#     address = models.CharField(max_length=200, blank=True , null=True)
#     phone = models.CharField(max_length=10, blank=True, null=True)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['name']

#     objects = CustomUserManager()


# class User(models.Model):
#     name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=100)

 # def create_superuser(self,email,name,password=None,address=None):
    #     user = self.create_user(
    #         email=email,
    #         name=name,
    #         address=address,
    #         password=password
    #     )
    #     user.is_superuser = True
    #     user.save(using=self._db)
    #     return user

