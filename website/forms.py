from django import forms
from .models import *
from django.forms.widgets import TimeInput
from django.core.validators import MinValueValidator

class AuctionSearchForm(forms.Form):
    search_query = forms.CharField(label='Search by title or address', max_length=255)

class AuctionItemForm(forms.ModelForm):
    class Meta:
        model = AuctionItem
        fields = ['title', 'description', 'address', 'start_price', 'image', 'sketchfab_script']
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
class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['slot1','slot2', 'slot3']
        widgets = {
            'slot1': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'slot2': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'slot3': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class RefundRequestForm(forms.ModelForm):
    class Meta:
        model = RefundRequest
        fields = ['reason', 'bank_branch', 'bank_account_number']