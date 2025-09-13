from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.conf import settings



class QuoteRequest(models.Model):
    destination = models.CharField(max_length=100)
    departure = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    email = models.EmailField()
    message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.destination}"


class CustomUserManager(BaseUserManager):
    def create_user(self, email=None, phone=None, password=None, **extra_fields):
        if not email and not phone:
            raise ValueError("The user must have either an email or a phone number")

        email = self.normalize_email(email) if email else None
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not email:
            raise ValueError('Superuser must have an email')
        return self.create_user(email=email, password=password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], null=True, blank=True)
    #date_of_birth = models.DateField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', default='default.png', blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email or self.phone

# core/models.py



    

class TourPackage(models.Model):
    name = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    includes = models.TextField(default='Hotel, food, sightseeing')
    image = models.ImageField(upload_to='tour_images/')

    def __str__(self):
        return self.name

class TourDate(models.Model):
    tour = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='dates')
    date = models.DateField()
    seats_available = models.PositiveIntegerField(default=30)

    class Meta:
        unique_together = ('tour', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.tour.name} - {self.date} ({self.seats_available} seats left)"


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tour = models.ForeignKey(TourPackage, on_delete=models.CASCADE)
    num_travelers = models.PositiveIntegerField()
    special_request = models.TextField(blank=True, null=True)
    tour_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    payment_status = models.CharField(
    max_length=20,
    choices=[
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    ],
    default='Pending'
    )

    def __str__(self):
        return f"{self.user.name} - {self.tour.name} - {self.created_at.strftime('%Y-%m-%d')}"


class Traveler(models.Model):
    booking = models.ForeignKey(Booking, related_name='travelers', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name} (Booking #{self.booking.id})"

