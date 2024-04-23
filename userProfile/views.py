from django.shortcuts import render,redirect
from .forms import *
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import logout
import random
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse


# Create your views here.
def home(request):
    return render(request,'userProfile/home.html')

def aboutUs(request):
    return render(request,'userProfile/aboutUs.html')  

def register(request):
    if request.method=="POST":
        form=RegitrationForm(request.POST)
        if form.is_valid():
            var=form.save(commit=False)
            var.user=request.user
            var.save()
            return redirect ('userProfile:home')
    else:
        form=RegitrationForm()
    return render(request,'userProfile/register.html',{'form':form})

def profile_view(request):
    try:
        profile = request.user.buyer_seller
    except:
        profile = None
    #get_object_or_404(Buyer_Seller, user=request.user)
    return render(request,'userProfile/profile_view.html',{'profile':profile})

"""
def profile_update_page(request):
    profile = Buyer_Seller.objects.get(user=request.user)

    if request.method == 'POST':
        form = RegitrationForm(request.POST, instance=profile)
        if form.is_valid():
            var=form.save(commit=False)
            var.user=request.user
            var.save()
            return redirect("userProfile:profile_view")
    else:
        form = RegitrationForm(instance=profile)

    return render(request, 'userProfile/profile_update.html', {'form': form})

"""

def profile_update(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Generate OTP
        otp = ''.join(random.choices('0123456789', k=6))
        # Send OTP to user's email
        send_mail(
            'OTP for Profile Update',
            f'Your OTP for profile update is: {otp}',
            settings.EMAIL_HOST_USER,
            [request.user.email],
            fail_silently=False,
        )
        # Store the OTP in the session
        request.session['otp'] = otp
        return redirect("userProfile:otp_verification")
    else:
        return redirect("userProfile:home")  # Redirect to login if user is not authenticated

def otp_verification(request):
    if request.method == 'POST':
        # Get the OTP entered by the user
        entered_otp = request.POST.get('otp')
        # Get the OTP stored in the session
        otp_in_session = request.session.get('otp')
        # Compare the entered OTP with the one stored in the session
        if entered_otp == otp_in_session:
            # OTP matches, allow the user to update the profile
            del request.session['otp']  # Remove the OTP from the session
            return redirect('userProfile:profile_update_page')
        else:
            # OTP does not match, display an error message
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect("userProfile:otp_verification")

    return render(request, 'userProfile/otp_verification.html')

def profile_update_page(request):
    profile = Buyer_Seller.objects.get(user=request.user)

    if request.method == 'POST':
        form = RegitrationForm(request.POST, instance=profile)
        if form.is_valid():
            var = form.save(commit=False)
            var.user = request.user
            var.save()
            return redirect("userProfile:profile_view")
        else:
            print(form.errors)  # Print form errors for debugging
    else:
        form = RegitrationForm(instance=profile)

    return render(request, 'userProfile/profile_update.html', {'form': form})


def ManageSlot(request):
    role = ProtectRole(request,'advisor')

    if not role:
        return redirect('/')

    slots = AdvisorSlot.objects.filter(user=request.user)

    # print(slots[0].booked_user_list.all())

    return render(request,'userProfile/manage_slot.html',{'slots':slots})


def CreateSlot(request):
    role = ProtectRole(request,'advisor')

    if not role:
        return redirect('/')


    if request.method == 'POST':
        form = CreateSlotForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/manage-slot')
    return render(request,'userProfile/create_slot.html',{})


def UpdateSlot(request, id):
    role = ProtectRole(request,'advisor')

    if not role:
        return redirect('/')
    slot = AdvisorSlot.objects.get(id=int(id))

    form = UpdateSlotForm(instance=slot)


    if request.method == 'POST':

        form2 = UpdateSlotForm(request.POST, instance=slot)

        if form2.is_valid():
            form2.save()
            return redirect('/manage-slot')

    return render(request,'userProfile/update_slot.html',{'slot':slot,'form':form})


def DeleteSlot(request, id):
    role = ProtectRole(request,'advisor')

    if not role:
        return redirect('/')

    slot = AdvisorSlot.objects.get(id=int(id))

    slot.delete()

    return redirect('/manage-slot')


def ProtectRole(request, role):

    if not request.user.is_authenticated:
        return False

    elif role == 'admin':
        if not request.user.is_superuser:
            return False
    
    elif role == 'advisor':
        if not request.user.is_staff:
            return False

    return True


def BookSlot(request, id):
    if request.user.is_authenticated:
        slot = AdvisorSlot.objects.get(id=int(id))
        if slot.total_user+1 > slot.max_user:
            return JsonResponse({"Error":"Max capacity reached"})
        else:
            if request.user in slot.booked_user_list.all():
                slot.total_user -= 1
                slot.booked_user_list.remove(request.user)
                slot.save()

                return JsonResponse({'success':'Slot Unbooked successfully'})
            else:
                slot.total_user += 1
                slot.booked_user_list.add(request.user)
                slot.save()

                return JsonResponse({'success':'Slot booked successfully'})

    else:
        return JsonResponse({"Error":"You need to login first"})
    
def search_properties(request):
    if request.method == 'GET':
        location = request.GET.get('location')
        property_type = request.GET.get('property_type')
        price_range = request.GET.get('price_range')
        min_size = request.GET.get('min_size')

        items = AuctionItem.objects.all()
        if location:
            items = items.filter(address__icontains=location)
        if property_type:
            items = items.filter(house_type=property_type)
        if price_range:
            items = items.filter(start_price__lte=price_range)
        if min_size:
            items = items.filter(house_size__gte=min_size)

        return render(request, 'userProfile/search_results.html', {'items': items})

    return render(request, 'home.html')