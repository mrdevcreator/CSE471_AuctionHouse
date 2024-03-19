from django.shortcuts import render,redirect
from .forms import *
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import logout
from website.models import AdvisorSlot

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
    profile = request.user.buyer_seller
    #get_object_or_404(Buyer_Seller, user=request.user)
    return render(request,'userProfile/profile_view.html',{'profile':profile})


def profile_update(request):
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
