from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    clinic_address = models.CharField(max_length=200)
    experience_years = models.IntegerField()
    bio = models.TextField()
    photo = models.ImageField(upload_to='photos/', default='photos/default.png')

    def __str__(self):
        return self.name

class Review(models.Model):
    doctor = models.ForeignKey(Doctor, related_name="reviews", on_delete=models.CASCADE)
    reviewer_name = models.CharField(max_length=100)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.doctor.name} by {self.reviewer_name}"

# models.py

class DoctorConnection(models.Model):
    from_doctor = models.ForeignKey(Doctor, related_name='sent_requests', on_delete=models.CASCADE)
    to_doctor = models.ForeignKey(Doctor, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=20,
                              choices=(('pending', 'Pending'), ('accepted', 'Accepted')))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_doctor', 'to_doctor')


class Message(models.Model):
    sender = models.ForeignKey(Doctor, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(Doctor, related_name='received_messages', on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # <-- Add this line!
