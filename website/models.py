from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

h_type = (
    ('Bunglow','Bunglow'),
    ('Duplex', 'Duplex'),
    ('Flat', 'Flat'),
    ('Normal', 'Normal')
)

class AuctionItem(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    address = models.CharField(max_length=255)
    start_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    image = models.ImageField(upload_to='auction_item_images/', blank=True, null=True)


    # Newly added fields
    house_size = models.IntegerField(null=True, blank=True)
    floor_count = models.IntegerField(null=True, blank=True)
    house_type = models.CharField(max_length=15, choices=h_type, null=True, blank=True)


    def is_live(self):
        return self.start_time <= timezone.now() <= self.end_time

    def is_upcoming(self):
        return self.start_time > timezone.now()

    def is_past(self):
        return self.end_time<timezone.now()

    def __str__(self):
        return self.title
    



d_type = (
    ('Sunday','Sunday'),
    ('Monday','Monday'),
    ('Tuesday','Tuesday'),
    ('Wednesday','Wednesday'),
    ('Thursday','Thursday'),
    ('Friday','Friday'),
    ('Saturday','Saturday')
)

class AdvisorSlot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="slot")

    day = models.CharField(max_length=20, choices=d_type)

    start_time = models.TimeField()
    end_time = models.TimeField()

    message = models.TextField(null=True,blank=True)

    max_user = models.IntegerField(default=10)

    total_user = models.IntegerField(default=0,null=True, blank=True)

    meet_link = models.CharField(max_length=300, null=True, blank=True)

    booked_user_list = models.ManyToManyField(User, blank=True,  related_name='booked_users')

    # pending_user_list = models.ManyToManyField(User,blank=True,  related_name='pending_users')


    def __str__(self):
        return f"{self.user.username}'s {self.day}'s slot"
