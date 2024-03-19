from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'website'

urlpatterns = [
    path('live-auction-items/', views.live_auction_items, name='live_auction_items'),
    path('upcoming-auction-items/', views.upcoming_auction_items, name='upcoming_auction_items'),
    path('past-auction-items/', views.past_auction_items, name='past_auction_items'),
    path('auction-detail/<int:item_id>/', views.auction_detail, name='auction_detail'),
    path('search-live-auctions/', views.search_live_auctions, name='search_live_auctions'),
    path('search-upcoming-auctions/', views.search_upcoming_auctions, name='search_upcoming_auctions'),
    path('search-past-auctions/', views.search_past_auctions, name='search_past_auctions'),
    path('create_auction/', views.create_auction, name='create_auction'),
    path('bidding/<int:item_id>/',views.bidding,name="bidding"),
    path('seller_rating/<int:item_id>/', views.seller_rating, name='seller_rating'),
    path('seller/<int:seller_id>/', views.seller_profile, name='seller_profile'),


    path('advisors/',views.Advisor_Page,name='advisors'),
    path('advisors/<str:id>',views.Advisor_Inside,name='advisorInside')

    # path('rating-already-submitted/', views.rating_already_submitted, name='rating_already_submitted'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)