from django.urls import path
from . import views

app_name = 'userProfile'

urlpatterns=[
    path('',views.home,name="home"),
    path('register/',views.register,name="register"),
    path("aboutUs/",views.aboutUs,name="aboutUs"),
    path("profile_view/",views.profile_view,name="profile_view"),
    path("profile_update/",views.profile_update,name="profile_update"),
    path('manage-slot/',views.ManageSlot, name='manageSlot'),
    path('create-slot/',views.CreateSlot, name='createSlot'),
    path('update-slot/<str:id>',views.UpdateSlot,name='updateSlot'),
    path('delete-slot/<str:id>',views.DeleteSlot, name='deleteSlot'),
    path('book-slot/<str:id>',views.BookSlot,name='bookSlot'),
    path('search/', views.search_properties, name='search_properties'),
    ]