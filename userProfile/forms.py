
from django import forms
from . models import *
from website.models import *

class RegitrationForm(forms.ModelForm):
    class Meta:
        model= Buyer_Seller
        fields=['phone','address']

class CreateSlotForm(forms.ModelForm):
    class Meta:
        model = AdvisorSlot
        fields = "__all__"
        


class UpdateSlotForm(forms.ModelForm):
    class Meta:
        model = AdvisorSlot
        fields = ['day','start_time','end_time','message','meet_link','max_user']