from django.db import models
from django.contrib.auth.models import User
from django.core.validators import EmailValidator

b_type = (
    ("Buyer","Buyer"),
    ("Seller","Seller"),
)
class Buyer_Seller(models.Model):
    user=models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    phone=models.CharField(max_length=11)
    address=models.CharField(max_length=100)
    ratings_sum = models.IntegerField(default=0)
    ratings_count = models.IntegerField(default=0)

    # Newly added
    # type = models.CharField(max_length=10, choices=b_type, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def average_rating(self):
        if self.ratings_count == 0:
            return 0
        return self.ratings_sum / self.ratings_count
    



# class Profile(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile")

#     name = models.CharField(max_length=250)
#     phone=models.CharField(max_length=11)
#     address=models.CharField(max_length=100)

    
