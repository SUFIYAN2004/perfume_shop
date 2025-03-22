from django.urls import path
from . import views
from .views import home, product_detail, add_to_cart, remove_from_cart, cart_view, cart_count, generate_bill,user_login, process_payment, checkout, track_order, user_logout, user_login, register, profile_view




urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart_view'),  
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),  
    path('checkout/', checkout, name='checkout'),
    path('cart/count/', cart_count, name='cart_count'), 
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path("cart/count/", views.cart_count, name="cart_count"),
    path('cart/buy/', generate_bill, name='generate_bill'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path("track_order/<int:order_id>/", views.track_order, name="track_order"), 
    path("contact/", views.contact, name="contact"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),  # Ensure user_logout is imported
    path("register/", register, name="register"),
    path("profile/", profile_view, name="profile"),
]
