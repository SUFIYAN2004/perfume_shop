from django.contrib import admin


from .models import Product, Cart, Category
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
