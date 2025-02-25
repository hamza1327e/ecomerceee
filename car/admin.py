from django.contrib import admin
from car.models import Contact, Product, Category, Order,Clothing,Size,Color,Review,User_profile


class AdminProduct(admin.ModelAdmin):
    list_display = ['name', 'price', 'category','created_at','updated_at']


class AdminCategory(admin.ModelAdmin):
    list_display = ['name']

class ClothingAdmin(AdminProduct):
    list_display = ('name', 'price', 'material', 'gender', 'category', 'created_at', 'updated_at')

admin.site.register(Product,AdminProduct)
admin.site.register(Category, AdminCategory)
admin.site.register(Clothing,ClothingAdmin)
admin.site.register(Order)
admin.site.register(Contact)
admin.site.register(Size)
admin.site.register(Color)
admin.site.register(Review)
admin.site.register(User_profile)