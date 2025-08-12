from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Avg
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Doctor, Review, DoctorConnection, Message
from .forms import DoctorForm, ReviewForm, SignUpForm


# === Home page with doctor search, sidebar context (with unread messages) ===
def home(request):
    doctors = Doctor.objects.all()
    search = request.GET.get('search', '')
    if search:
        doctors = doctors.filter(
            Q(name__icontains=search) | Q(specialty__icontains=search) | Q(clinic_address__icontains=search)
        )

    # Sidebar context
    connected_doctors = []
    pending_requests = []
    unread_messages = []

    if request.user.is_authenticated and hasattr(request.user, 'doctor'):
        doctor = request.user.doctor

        connected_doctors = DoctorConnection.objects.filter(
            Q(from_doctor=doctor) | Q(to_doctor=doctor), status='accepted'
        )

        pending_requests = DoctorConnection.objects.filter(
            Q(from_doctor=doctor) | Q(to_doctor=doctor), status='pending'
        )

        unread_messages = Message.objects.filter(
            recipient=doctor, is_read=False
        ).order_by('-timestamp')

    context = {
        'doctors': doctors,
        'connected_doctors': connected_doctors,
        'pending_requests': pending_requests,
        'unread_messages': unread_messages,
    }
    return render(request, 'home.html', context)


# === Doctor profile view (with reviews, connect/chat actions) ===
def doctor_profile(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    reviews = doctor.reviews.order_by('-created_at')[:10]
    connected = False
    connection_pending = False

    if request.user.is_authenticated and hasattr(request.user, 'doctor'):
        me = request.user.doctor
        connected = DoctorConnection.objects.filter(
            Q(from_doctor=me, to_doctor=doctor, status='accepted') |
            Q(from_doctor=doctor, to_doctor=me, status='accepted')
        ).exists()
        connection_pending = DoctorConnection.objects.filter(
            from_doctor=me, to_doctor=doctor, status='pending'
        ).exists()

    # Add a review
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.doctor = doctor
            review.save()
            return redirect('doctor_profile', doctor_id=doctor.id)
    else:
        form = ReviewForm()

    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    return render(request, 'doctor_profile.html', {
        'doctor': doctor,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'form': form,
        'connected': connected,
        'connection_pending': connection_pending,
    })


# === Signup view ===
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('register_doctor')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


# === Register Doctor ===
@login_required
def register_doctor(request):
    if hasattr(request.user, 'doctor'):
        return redirect('doctor_profile', doctor_id=request.user.doctor.id)
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.user = request.user
            doctor.save()
            return redirect('doctor_profile', doctor_id=doctor.id)
    else:
        form = DoctorForm()
    return render(request, 'register_doctor.html', {'form': form})


# === Edit Doctor Profile ===
@login_required
def edit_doctor(request):
    doctor = Doctor.objects.get(user=request.user)
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect('doctor_profile', doctor_id=doctor.id)
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'edit_doctor.html', {'form': form, 'doctor': doctor})


# === Logout ===
def user_logout(request):
    logout(request)
    return redirect('home')


# === Send Connection Request ===
@login_required
def send_connection_request(request, doctor_id):
    from_doctor = request.user.doctor
    to_doctor = get_object_or_404(Doctor, id=doctor_id)
    if from_doctor != to_doctor:
        DoctorConnection.objects.get_or_create(from_doctor=from_doctor, to_doctor=to_doctor, status='pending')
    return redirect('doctor_profile', doctor_id=doctor_id)


# === Accept Connection Request ===
@login_required
def accept_connection_request(request, conn_id):
    connection = get_object_or_404(DoctorConnection, id=conn_id, to_doctor=request.user.doctor, status='pending')
    connection.status = 'accepted'
    connection.save()
    return redirect('doctor_profile', doctor_id=connection.from_doctor.id)


# === Chat view with attachments and marks messages as read on open ===
@login_required
def chat_view(request, doctor_id):
    me = request.user.doctor
    other_doctor = get_object_or_404(Doctor, id=doctor_id)

    # Mark all unread messages from other_doctor as read (when chat is opened)
    Message.objects.filter(sender=other_doctor, recipient=me, is_read=False).update(is_read=True)

    if request.method == "POST":
        text = request.POST.get('text', '').strip()
        file = request.FILES.get('attachment', None)
        Message.objects.create(
            sender=me,
            recipient=other_doctor,
            text=text,
            attachment=file if file else None,
            is_read=False,  # Message is unread for recipient automatically
        )
        return redirect('chat', doctor_id=other_doctor.id)

    messages = Message.objects.filter(
        Q(sender=me, recipient=other_doctor) | Q(sender=other_doctor, recipient=me)
    ).order_by('timestamp')
    return render(request, "chat.html", {"messages": messages, "other_doctor": other_doctor})


# Compatibility for old 'chat' view name
chat = chat_view


# === Login view (fixes last-line syntax error) ===
def doctor_login(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = "Invalid username or password"
    return render(request, "login.html", {"error": error})
