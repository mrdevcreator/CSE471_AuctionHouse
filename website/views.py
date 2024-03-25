# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import AuctionItem, AdvisorSlot
from .forms import * 
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from userProfile.models import Buyer_Seller
from django.contrib.auth.models import User


# Staff users common password - ilovecat

def live_auction_items(request):
    current_time = timezone.now()
    # Live Auctions
    live_auctions = AuctionItem.objects.filter(start_time__lte=current_time, end_time__gt=current_time)

    return render(request, 'live_auction_items.html', {
        'live_auctions': live_auctions,
    })


def upcoming_auction_items(request):
    current_time = timezone.now()

    upcoming_auctions = AuctionItem.objects.filter(start_time__gt=current_time, end_time__gt=current_time)

    return render(request, 'upcoming_auction_items.html', {
        'upcoming_auctions': upcoming_auctions,
    })

def past_auction_items(request):
    current_time = timezone.now()

    past_auctions = AuctionItem.objects.filter(start_time__lt=current_time,end_time__lt=current_time)

    return render(request, 'past_auction_items.html', {
        'past_auctions': past_auctions,
    })


def auction_detail(request, item_id):
    auction_detail = get_object_or_404(AuctionItem, id=item_id)

    # Get bid history for similar properties in the same area
    similar_auctions = AuctionItem.objects.filter(
        Q(address__icontains=auction_detail.address) and
        Q(house_type=auction_detail.house_type)
    ).exclude(id=auction_detail.id)

    if (len(similar_auctions) >= 5):
        similar_auctions = similar_auctions[:5]


    return render(request, 'auction_detail.html', {'auction_detail': auction_detail,'similar_auctions': similar_auctions})


def search_live_auctions(request):
    query = request.GET.get('query', '')
    current_time = timezone.now()

    # checks if the query is in the title or address of the auction item
    live_auctions = AuctionItem.objects.filter(
        Q(title__icontains=query) | Q(address__icontains=query),
        end_time__gte=current_time
    )

    return render(request, 'auction_search.html', {'auctions': live_auctions, 'query': query, 'search_type': 'Live Auctions'})

def search_upcoming_auctions(request):
    query = request.GET.get('query', '')
    current_time = timezone.now()

    upcoming_auctions = AuctionItem.objects.filter(
        Q(title__icontains=query) | Q(address__icontains=query),
        start_time__gt=current_time,
    )

    return render(request, 'auction_search.html', {'auctions': upcoming_auctions, 'query': query, 'search_type': 'Upcoming Auctions'})


def search_past_auctions(request):
    query = request.GET.get('query', '')
    current_time = timezone.now()

    past_auctions = AuctionItem.objects.filter(
        Q(title__icontains=query) | Q(address__icontains=query),
        end_time__lt=current_time
    )

    return render(request, 'auction_search.html', {'auctions': past_auctions, 'query': query, 'search_type': 'Past Auctions'})


    
@login_required 
def create_auction(request):
    if request.method == 'POST':
        form = AuctionItemForm(request.POST, request.FILES)
        if form.is_valid():
            auction_item = form.save(commit=False)
            auction_item.created_by = request.user
            auction_item.save()
            return redirect('website:auction_detail', item_id=auction_item.id)
    else:
        form = AuctionItemForm()

    return render(request, 'create_auction.html', {'form': form})

def bidding(request, item_id):
    auction = get_object_or_404(AuctionItem, id=item_id)

    s_a = AuctionItem.objects.filter(
        Q(address__icontains=auction.address) and
        Q(house_type=auction.house_type) and
        Q(end_time__gt=timezone.now()) and 
        Q(current_bid__gt=0)
    )

    avg_per_sq_feet_price = 0
    avg_per_floor_price = 0
    count = 0
    for auctions in s_a:
        avg_per_sq_feet_price += (auctions.current_bid / auctions.house_size)
        avg_per_floor_price += (auctions.current_bid / auctions.floor_count)
        count += 1
    
    avg_per_floor_price = avg_per_floor_price / count 
    avg_per_sq_feet_price = avg_per_sq_feet_price / count

    predicted_value = (auction.house_size * avg_per_sq_feet_price + auction.floor_count * avg_per_floor_price) / 2


    predicted_value = int(predicted_value)
    
    if request.method=="POST":
        form=BiddingForm(request.POST)
        if form.is_valid():
            bid_amount = form.cleaned_data['current_bid']
            if bid_amount > auction.current_bid and bid_amount > auction.start_price:
                auction.current_bid = bid_amount
                auction.save()
                return redirect('website:live_auction_items')
            else:
                message = 'Your bid should be greater than the current bid and starting price.'
                return render(request, 'bidding.html', {'auction': auction, 'form': form, 'message': message,'predicted_value':predicted_value})
    else:
        form=BiddingForm
    return render(request,'bidding.html',{'auction': auction,'form':form,'predicted_value':predicted_value})
        

def seller_rating(request, item_id):
    auction = get_object_or_404(AuctionItem, id=item_id)
    seller = auction.created_by.buyer_seller

    if request.method == "POST":
        rating = int(request.POST.get('rating'))

        seller.ratings_sum += rating
        seller.ratings_count += 1
        seller.save()

        return redirect('website:live_auction_items')

    return render(request, 'seller_rating.html', {'seller': seller, 'auction': auction})

def seller_profile(request, seller_id):
    seller = get_object_or_404(Buyer_Seller, user_id=seller_id)
    return render(request, 'seller_profile.html', {'seller': seller})


def Advisor_Page(request):

    advisors = User.objects.filter(is_staff=True).exclude(is_superuser=True)

    return render(request,'advisor_page.html',{'advisors':advisors})


def Advisor_Inside(request,id):
    advisor = get_object_or_404(User, id=int(id))

    slots = AdvisorSlot.objects.filter(user=advisor)

    return render(request,'advisor_inside.html',{'advisor':advisor,'slots':slots})