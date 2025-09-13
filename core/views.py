import razorpay
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import QuoteRequest,CustomUser, TourPackage, Booking, Traveler, TourDate
from .forms import QuoteRequestForm, LoginForm, SignupForm, ProfileUpdateForm, UserUpdateForm, TravelerForm, BookingForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from datetime import datetime, timedelta
from .utils import generate_booking_pdf
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone





User = get_user_model()




# Create your views here.
def home(request):
    return render(request,"home.html")

def feedback(request):
    return render(request,"feedback.html")

def feedback2(request):
    return render(request,"feedback2.html")

def bottom(request):
    return render(request,"bottom.html")

def middle(request):
    return render(request,"middle.html")

def top(request):
    return render(request,"top.html")

def mybookings(request):
    return render(request,"mybookings.html")


def packages(request):
    tours = TourPackage.objects.annotate(total_seats=Sum('dates__seats_available'))
    return render(request, 'packages.html', {'tours': tours})

@login_required
def booknow(request, tour_id):
    tour = get_object_or_404(TourPackage, id=tour_id)

     # cutoff = 24 hours from now
    cutoff = timezone.now() + timedelta(hours=24)

    available_dates = TourDate.objects.filter(tour=tour, seats_available__gt=0,date__gte=cutoff.date()).order_by('date')

    seat_info = {date_obj.date.strftime("%Y-%m-%d"): date_obj.seats_available for date_obj in available_dates
    }

    
    

    if request.method == 'POST':
        num_travelers = int(request.POST.get('num_travelers', 1))
        special_request = request.POST.get('special_request', '')
        # tour_date = request.POST.get('tour_date')
        selected_date_id = request.POST.get('tour_date')

        try:
            tour_date_obj = TourDate.objects.get(id=selected_date_id, tour=tour)
            selected_date = tour_date_obj.date


        except TourDate.DoesNotExist:
            return render(request, 'booknow.html', {
                'tour': tour,
                'available_dates': available_dates,
                'seat_info': seat_info,
                'error': 'Invalid tour date selected.',
                'traveler_range': range(10),
                'traveler_count_choices': range(1, 11),
                'booking_form': BookingForm(),
            })
        selected_date = tour_date_obj.date 

        if tour_date_obj.seats_available < num_travelers:
            return render(request, 'booknow.html', {
                'tour': tour,
                'available_dates': available_dates,
                'seat_info': seat_info,
                'error': f'Only {tour_date_obj.seats_available} seats available on {tour_date_obj.date}. Please choose fewer travelers or another date.',
                'traveler_range': range(10),
                'traveler_count_choices': range(1, 11),
                'booking_form': BookingForm(),
                })
        
        travelers = []
        

        for i in range(num_travelers):
            name = request.POST.get(f'traveler_name_{i}', '').strip()
            age = request.POST.get(f'traveler_age_{i}', '').strip()
            email = request.POST.get(f'traveler_email_{i}', '').strip()
            phone = request.POST.get(f'traveler_phone_{i}', '').strip()

            if name and age and email and phone:
                travelers.append({
                    'name': name,
                    'age': age,
                    'email': email,
                    'phone': phone
                })
            else:
                return render(request, 'booknow.html', {
                    'tour': tour,
                    'available_dates': available_dates,
                    'seat_info': seat_info,
                    'error': f'Missing details for traveler {i + 1}. Please fill out all fields.',
                    'traveler_range': range(10),
                    'traveler_count_choices': range(1, 11),
                    'booking_form': BookingForm(),
                })



        total_amount = int(tour.price * num_travelers * 100)




        # Create Booking
        booking = Booking.objects.create(
            user=request.user,
            tour=tour,
            special_request=special_request,
            total_amount=total_amount / 100,
            num_travelers=num_travelers,
            tour_date=selected_date
        )

        # Reduce available seats
        tour_date_obj.seats_available -= num_travelers
        tour_date_obj.save()

        traveler_emails = []
        for traveler_data in travelers:
            Traveler.objects.create(
                booking=booking,
                name=traveler_data['name'],
                age=traveler_data['age'],
                email=traveler_data['email'],
                phone=traveler_data['phone']
            )
            traveler_emails.append(traveler_data['email']) 
       

        # Razorpay Order
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create(dict(
            amount=total_amount,
            currency='INR',
            payment_capture='1'
        ))

        booking.razorpay_order_id = razorpay_order['id']
        booking.save()



        return render(request, 'payment_page.html', {
            'booking': booking,
            'tour': tour,
            'order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount': int(total_amount),  # in paisa, already * 100

        })

    return render(request, 'booknow.html', {
        'tour': tour,
        'available_dates': available_dates,
        'seat_info': seat_info,
        'traveler_range': range(10),                # for 10 rows in table
        'traveler_count_choices': range(1, 11),     # for dropdown (1 to 10)
        'booking_form': BookingForm(),
        })




def get_quote(request):
    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your request has been submitted successfully.")
            return render(request, 'contact_form.html', {'form': QuoteRequestForm()})  # 👈 reload same page
    else:
        form = QuoteRequestForm()
    return render(request, 'contact_form.html', {'form': form})


def custom_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        identifier = form.cleaned_data['identifier']
        password = form.cleaned_data['password']

        user = None
        try:
            user = CustomUser.objects.get(email=identifier)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(phone=identifier)
            except CustomUser.DoesNotExist:
                user = None

        if user:
            user = authenticate(request, email=user.email, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid credentials.")
        else:
            messages.error(request, "User not found.")

    return render(request, 'login.html', {'form': form})

            

@login_required
def custom_logout(request):
    logout(request)
    return redirect('login')

def custom_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Signup successful! Please login.")
            return redirect('login')
        else:
            messages.error(request, "There were errors in your form. Please fix them.")
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})




@login_required
def personal_info(request):
    user = request.user

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('personalinfo')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, 'personalinfo.html', {'form': form})



@login_required
@csrf_exempt
def update_personal_info_ajax(request):
    if request.method == 'POST':
        user = request.user
        field = request.POST.get('field')
        value = request.POST.get('value')

        if field in ['name', 'email', 'phone', 'dob', 'gender']:
            setattr(user, field, value)
            user.save()
            return JsonResponse({'status': 'success', 'field': field, 'value': value})
        return JsonResponse({'status': 'error', 'message': 'Invalid field'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def upload_profile_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        user = request.user
        user.profile_photo = request.FILES['photo']
        user.save()
        return JsonResponse({'status': 'success', 'photo_url': user.profile_photo.url})
    return JsonResponse({'status': 'error'})



# core/views.py



@login_required
def payment_details(request, tour_id):
    tour = get_object_or_404(TourPackage, id=tour_id)

    if request.method == 'POST':
        num_travelers = int(request.POST.get('num_travelers', 1))
        booking_form = BookingForm(request.POST)

        traveler_forms = [
            TravelerForm(request.POST, prefix=str(i))
            for i in range(num_travelers)
        ]

        if booking_form.is_valid() and all(f.is_valid() for f in traveler_forms):
            booking = booking_form.save(commit=False)
            booking.user = request.user
            booking.tour = tour
            booking.total_price = tour.price_per_person * num_travelers
            booking.save()

            for f in traveler_forms:
                traveler = f.save(commit=False)
                traveler.booking = booking
                traveler.save()

            # [🔁 Next Step: Razorpay integration goes here]

            messages.success(request, 'Booking created. Redirecting to payment...')
            return redirect('packages')  # or redirect to Razorpay gateway

    else:
        booking_form = BookingForm()
        traveler_forms = [TravelerForm(prefix='0')]

    return render(request, 'payment_details.html', {
        'tour': tour,
        'booking_form': booking_form,
        'traveler_forms': traveler_forms
    })




def payment_success(request, booking_id):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')

        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        booking.razorpay_payment_id = payment_id
        booking.payment_status = 'Paid'
        booking.save()

        travelers = booking.travelers.all()
        tour = booking.tour

        # ✅ Generate PDF once
        pdf_buffer = generate_booking_pdf(booking, travelers, tour)

        # ✅ Send confirmation emails to travelers with PDF attached
        for traveler in travelers:
            email = EmailMessage(
                subject="Booking Confirmed!",
                body=f"Hello {traveler.name},\n\nYour tour '{tour.name}' has been successfully booked.\nTour duration: {tour.duration}\nAmount: ₹{booking.total_amount}.\n\nAttached is your booking confirmation.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[traveler.email],
            )
            email.attach(f"Booking_{booking.id}.pdf", pdf_buffer.getvalue(), "application/pdf")
            email.send()

        # ✅ Send confirmation to the booking user with PDF attached
        user_email = EmailMessage(
            subject="Tour Booking Success",
            body=f"Dear {request.user.name},\n\nYour booking for '{tour.name}' has been successfully processed.\nTotal Travelers: {travelers.count()}\nTotal Amount: ₹{booking.total_amount}.\n\nAttached is your booking confirmation.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[request.user.email],
        )
        user_email.attach(f"Booking_{booking.id}.pdf", pdf_buffer.getvalue(), "application/pdf")
        user_email.send()

        return render(request, 'confirmation.html', {'booking': booking})

    return redirect('packages')


#Downloadable PDF
@login_required
def download_booking_pdf(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    booking.refresh_from_db()

    travelers = Traveler.objects.filter(booking=booking)
    tour = booking.tour

    pdf_buffer = generate_booking_pdf(booking, travelers, tour)

    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Booking_{booking.id}.pdf"'
    return response






def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('identifier')
        try:
            user = User.objects.get(email=email)  # Now works with CustomUser
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(f"/reset-password/{uid}/{token}/")

            subject = "Password Reset Request"
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'reset_link': reset_link
            })
            send_mail(subject, message, 'noreply@rocketsingh.com', [email])

            messages.success(request, "Password reset link has been sent to your email.")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")
    return render(request, "forgot_password.html")



def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if not new_password or not confirm_password:
                messages.error(request, "Please fill in both password fields.")
            elif new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
            else:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password reset successful! Please log in.")
                return redirect("login")
        return render(request, "reset_password.html", {"validlink": True})
    
    # Only show error if link truly invalid
    return render(request, "reset_password.html", {
        "validlink": False
    })

# Change password for logged-in users
@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not request.user.has_usable_password():
            # Google/social login user → skip old password check
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
            else:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, "Password set successfully.")
                return redirect("login")

        else:
            if not request.user.check_password(old_password):
                messages.error(request, "Old password is incorrect.")

            elif new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
            
            else:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, "Password changed successfully.")
                return redirect('login')

    return render(request, "change_password.html")



from django.utils.timezone import now

@login_required
def my_bookings(request):
    today = now().date()

    # Only future bookings and not cancelled
    upcoming_bookings = Booking.objects.filter(
        user=request.user,
        tour_date__gte=today,
    ).exclude(payment_status="Cancelled").order_by("tour_date")

    # Past/completed/cancelled bookings
    cancelled_bookings = Booking.objects.filter(
        user=request.user,
        payment_status="Cancelled"
    ).order_by("-tour_date")

    past_bookings = Booking.objects.filter(
        user=request.user,
        tour_date__lt=today,
        payment_status="Paid"
    ).order_by("-tour_date")

    return render(request, "mybookings.html", {
        "upcoming_bookings": upcoming_bookings,
        "cancelled_bookings": cancelled_bookings,
        "past_bookings": past_bookings,
    })


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'booking_detail.html', {'booking': booking})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Prevent cancelling past bookings
    if booking.tour_date < now().date():
        messages.error(request, "You cannot cancel a past booking.")
        return redirect('mybookings')

    if request.method == "POST":
        booking.payment_status = "Cancelled"
        booking.save()
        messages.success(request, "Your booking has been cancelled.")
        return redirect('mybookings')

    # Show confirmation page
    return render(request, 'cancel_booking.html', {
        "booking": booking,
        "today": now().date(),})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import ProfileCompletionForm

User = get_user_model()

@login_required
def profile_check(request):
    """After any login (including Google), send user to complete profile if needed."""
    user = request.user
    missing = []
    for field in ["name", "gender", "dob", "phone"]:  # adjust to your CustomUser fields
        if not getattr(user, field, None):
            missing.append(field)

    if missing:
        messages.info(request, "Please complete your profile to continue.")
        return redirect("complete_profile")

    # otherwise go wherever you prefer
    return redirect("home")  # or 'dashboard' or 'mybookings'
    

@login_required
def complete_profile(request):
    user = request.user
    if request.method == "POST":
        form = ProfileCompletionForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("home")  # or wherever
    else:
        form = ProfileCompletionForm(instance=user)
    return render(request, "complete_profile.html", {"form": form})
