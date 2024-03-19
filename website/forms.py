from django import forms
from .models import AuctionItem
from django.forms.widgets import TimeInput
from django.core.validators import MinValueValidator

class AuctionSearchForm(forms.Form):
    search_query = forms.CharField(label='Search by title or address', max_length=255)

class AuctionItemForm(forms.ModelForm):
    class Meta:
        model = AuctionItem
        fields = ['title', 'description', 'address', 'start_price', 'start_time', 'end_time', 'image']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class BiddingForm(forms.ModelForm):
    class Meta:
        model = AuctionItem
        fields=['current_bid']
        labels = {
            'current_bid': 'Enter your Bid :',
        }