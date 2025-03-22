from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Product, Category, CartItem
import json
from datetime import datetime, timedelta 
from django.urls import reverse  # Add this!
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required



def home(request):
    query = request.GET.get('q', '')  # Get search query
    category_id = request.GET.get('category')  # Get category filter from URL

    if query:
        products = Product.objects.filter(name__icontains=query)  # Search in product names
    elif category_id:
        products = Product.objects.filter(category_id=category_id)  # Filter by category
    else:
        products = Product.objects.all()  # Show all products

    categories = Category.objects.all()
    cart_count = request.session.get('cart_count', 0)

    context = {
        'products': products,
        'categories': categories,
        'cart_count': cart_count,
        'query': query  # Pass search query to template
    }
    return render(request, 'shop/home.html', context)




def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    related_products = Product.objects.exclude(id=product.id)[:4]  # Show 4 related products

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'cart_count': sum(item['quantity'] for item in request.session.get('cart', {}).values())
    })


def add_to_cart(request, product_id):
    if request.method == "POST":
        try:
            cart = request.session.get('cart', {})

            # Get product details
            product = get_object_or_404(Product, id=product_id)

            # Load and validate JSON data
            try:
                data = json.loads(request.body)
                quantity = int(data.get("quantity", 1))  # Default to 1
                if quantity < 1:
                    return JsonResponse({'error': 'Invalid quantity'}, status=400)
            except (json.JSONDecodeError, ValueError):
                return JsonResponse({'error': 'Invalid request data'}, status=400)

            # Add/update product in cart
            product_id_str = str(product_id)
            if product_id_str in cart:
                cart[product_id_str]['quantity'] += quantity
            else:
                cart[product_id_str] = {
                    'name': product.name,
                    'price': float(product.price),  # Convert Decimal to float
                    'quantity': quantity
                }

            # Update session
            request.session['cart'] = cart
            request.session.modified = True

            return JsonResponse({'cart': cart, 'cart_count': sum(item['quantity'] for item in cart.values())})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)




def cart_view(request):
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = 0

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * item["quantity"]
            cart_items.append({
                'product': product,
                'quantity': item["quantity"],
                'total': item_total
            })
            total_price += item_total
        except Product.DoesNotExist:
            # If the product is not found, remove it from the session
            del cart[product_id]

    request.session['cart'] = cart  # Ensure session is updated
    request.session.modified = True

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })



def checkout(request):
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = 0

    if cart:
        for product_id, item in cart.items():
            product = Product.objects.get(id=product_id)
            subtotal = item['quantity'] * product.price
            total_price += subtotal

            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'subtotal': subtotal
            })

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }

    return render(request, 'shop/checkout.html', context)



def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]  # Remove product from cart

        # ✅ Immediately save the session update
        request.session['cart'] = cart  
        request.session.modified = True  

    # ✅ Ensure fresh cart count is sent
    cart_count = sum(item['quantity'] for item in cart.values())

    return JsonResponse({'cart': cart, 'cart_count': cart_count})


def cart_count(request):
    cart = request.session.get('cart', {})
    total_items = sum(item['quantity'] for item in cart.values())  # Sum quantities of all products
    return JsonResponse({"cart_count": total_items})

def generate_bill(request):
    cart = request.session.get('cart', {})
    
    cart_items = []
    total_price = 0

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * item["quantity"]
            cart_items.append({
                'name': product.name,
                'quantity': item["quantity"],
                'total': item_total
            })
            total_price += item_total
        except Product.DoesNotExist:
            del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return JsonResponse({'cart_items': cart_items, 'total_price': total_price})

    
def track_order(request, order_id):
    return render(request, "shop/track_order.html", {"order_id": order_id})

def process_payment(request):
    order_id = 12345  # Example order ID, replace with actual logic
    return redirect(reverse("track_order", kwargs={"order_id": order_id}))


def contact(request):
    return render(request, "shop/contact.html")

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")  # Redirect to home page after login
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, "shop/login.html")  # Use "shop/" prefix

# Logout View
def user_logout(request):
    logout(request)
    return redirect("home")

# Register View
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect("home")  # Redirect to home page after signup
    
    return render(request, "shop/register.html")  # Use "shop/" prefix

@login_required
def profile_view(request):
    return render(request, "shop/profile.html")
