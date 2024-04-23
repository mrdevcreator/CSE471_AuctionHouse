from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import AuctionItem,Wishlist, Bid
from .forms import * 
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from userProfile.models import Buyer_Seller, Rating
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
from django.http import HttpResponse


def live_auction_items(request):
    current_time = timezone.now()
    live_auctions = AuctionItem.objects.filter(approval_status='approved', start_time__lte=current_time, end_time__gt=current_time)
    return render(request, 'live_auction_items.html', {'live_auctions': live_auctions})


def upcoming_auction_items(request):
    current_time = timezone.now()

    upcoming_auctions = AuctionItem.objects.filter(start_time__gt=current_time, end_time__gt=current_time, approval_status='approved')

    return render(request, 'upcoming_auction_items.html', {
        'upcoming_auctions': upcoming_auctions,
    })

def past_auction_items(request=None):
    current_time = timezone.now()
    past_auctions = AuctionItem.objects.filter(start_time__lt=current_time, end_time__lt=current_time, approval_status='approved')

    for auction in past_auctions:
        if not auction.winner:  
            auction.determine_winner() 

    if request:
        return render(request, 'past_auction_items.html', {
            'past_auctions': past_auctions,
        })
        
    else:
        return past_auctions

def auction_detail(request, item_id):
    auction_detail = get_object_or_404(AuctionItem, id=item_id)
    similar_auctions = AuctionItem.objects.filter(
        Q(address__icontains=auction_detail.address) and
        Q(house_type=auction_detail.house_type)
    ).exclude(id=auction_detail.id)

    if (len(similar_auctions) >= 5):
        similar_auctions = similar_auctions[:5]

    if auction_detail.is_past() and not auction_detail.winner:
        auction_detail.determine_winner()
        
    return render(request, 'auction_detail.html', {'auction_detail': auction_detail,'similar_auctions': similar_auctions})


def search_live_auctions(request):
    query = request.GET.get('query', '')
    current_time = timezone.now()
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
            auction_item.approval_status = 'pending'
            auction_item.save()
            return redirect('website:auction_detail', item_id=auction_item.id)
    else:
        form = AuctionItemForm()

    return render(request, 'create_auction.html', {'form': form})



@login_required
def bidding(request, item_id):
    auction = get_object_or_404(AuctionItem, id=item_id)
    s_a = AuctionItem.objects.filter(
        Q(address__icontains=auction.address) and
        Q(house_type=auction.house_type) and
        Q(end_time__gt=timezone.now()) and 
        Q(current_bid__gt=0)
    )

    avg_per_sq_feet_price = Decimal(0)
    avg_per_floor_price = Decimal(0)
    count = 0

    if s_a.exists():  # Check if the queryset is not empty
        for auctions in s_a:
            if auctions.house_size:
                avg_per_sq_feet_price += (auctions.current_bid / auctions.house_size)
            if auctions.floor_count:
                avg_per_floor_price += (auctions.current_bid / auctions.floor_count)
            count += 1
        
        if count > 0:
            avg_per_floor_price = avg_per_floor_price / count 
            avg_per_sq_feet_price = avg_per_sq_feet_price / count

            predicted_value = (auction.house_size * avg_per_sq_feet_price + auction.floor_count * avg_per_floor_price) / 2
            predicted_value = int(predicted_value)
        else:
            predicted_value = None  # Set predicted_value to None if there are no valid auctions
    else:
        predicted_value = None

    if request.method == "POST":
        form = BiddingForm(request.POST)
        if form.is_valid():
            bid_amount = form.cleaned_data['current_bid']

            # Get the current highest bid for the auction
            highest_bid = Bid.objects.filter(item=auction).order_by('-amount').first()

            if bid_amount >= auction.start_price and (not highest_bid or bid_amount > highest_bid.amount):
                previous_highest_bidder = highest_bid.bidder if highest_bid else None  
                new_bid = Bid.objects.create(bidder=request.user, item=auction, amount=bid_amount)  

                auction.current_bid_by = new_bid.bidder
                auction.current_bid = new_bid.amount
                auction.save()

                if previous_highest_bidder:
                    send_outbid_email(previous_highest_bidder, auction.title, bid_amount)  # Send outbid email

                return redirect('website:live_auction_items')
                
            else:
                message = 'Your bid should be greater than the starting price and the current highest bid.'
                return render(request, 'bidding.html', {'auction': auction, 'form': form, 'message': message, 'predicted_value':predicted_value})
    else:
        form = BiddingForm()
    return render(request, 'bidding.html', {'auction': auction, 'form': form, 'predicted_value':predicted_value})

def send_outbid_email(previous_highest_bidder, auction_title, current_highest_bid):
    subject = 'Your bid has been outbid!'
    message = render_to_string('outbid_email.html', {'auction_title': auction_title,'previous_highest_bidder':previous_highest_bidder,'current_highest_bid':current_highest_bid})
    send_mail(subject, message, settings.EMAIL_HOST_USER, [previous_highest_bidder.email])

def seller_rating(request, item_id):
    auction = get_object_or_404(AuctionItem, id=item_id)
    buyer_seller = auction.created_by.buyer_seller

    if request.method == "POST":
        rating_value = int(request.POST.get('rating'))

        # Checking if the user has already rated this item
        if not Rating.objects.filter(buyer_seller=buyer_seller, item=auction).exists():
            rating = Rating.objects.create(buyer_seller=buyer_seller, item=auction, rating=rating_value)
            return redirect('website:live_auction_items')
        else:
            return render(request, 'rating_already_submitted.html', {'buyer_seller': buyer_seller, 'auction': auction})

    return render(request, 'seller_rating.html', {'buyer_seller': buyer_seller, 'auction': auction})

def seller_profile(request, seller_id):
    seller = get_object_or_404(Buyer_Seller, user_id=seller_id)
    return render(request, 'seller_profile.html', {'seller': seller})



def add_to_wishlist(request, item_id):
    wish = get_object_or_404(AuctionItem, id=item_id)
    new_object = Wishlist.objects.create(creator=request.user, wish=wish)
    return redirect('website:show_wishlist')

def show_wishlist(request):
    wishlist = Wishlist.objects.filter(creator=request.user)
    return render(request, 'wishlist.html', {'wishlist': wishlist})

def winner_me(request):
    current_time = timezone.now()

    past_auctions = AuctionItem.objects.filter(start_time__lt=current_time,end_time__lt=current_time,current_bid_by=request.user)

    return render(request, 'winner_me.html', {
        'past_auctions': past_auctions,
    })


def meeting(request, item_id):
    auction = get_object_or_404(AuctionItem, id=item_id)
    if request.method == 'POST':
        form = MeetingForm(request.POST, request.FILES)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.item=auction
            meeting.owner=auction.created_by 
            meeting.winner= request.user
            meeting.save()
            title=auction.title
            send_meeting_email(title,meeting.slot1,meeting.slot2,meeting.slot3,meeting.owner,meeting.winner)
            return redirect('userProfile:home')
    else:
        form = MeetingForm()

    return render(request, 'meeting.html', {'form': form})

def send_meeting_email(auction,slot1,slot2,slot3,owner,winner):
    subject = 'Winner wants to schedule a meeting!'
    message = render_to_string('meeting_email.html', {'auction': auction,'slot1':slot1,'slot2':slot2,'slot3':slot3,'owner':owner,'winner':winner})
    send_mail(subject, message, settings.EMAIL_HOST_USER, [owner.email])

# saha
def Advisor_Page(request):

    advisors = User.objects.filter(is_staff=True).exclude(is_superuser=True)

    return render(request,'advisor_page.html',{'advisors':advisors})


def Advisor_Inside(request,id):
    advisor = get_object_or_404(User, id=int(id))

    slots = AdvisorSlot.objects.filter(user=advisor)

    return render(request,'advisor_inside.html',{'advisor':advisor,'slots':slots})

def refund_request(request):
    if request.method == 'POST':
        form = RefundRequestForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect('userProfile:home')  # Redirect to a success page
    else:
        form = RefundRequestForm()
    return render(request, 'refund.html', {'form': form})

def generate_bill(request):
    context = {
        'customer_name': request.user,
        'total_amount': 100000.00,
        
    }
    html_content = render_to_string('bill_template.html', context)
 
    return HttpResponse(html_content, content_type='text/html')