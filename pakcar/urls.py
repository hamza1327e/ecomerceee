from django.contrib import admin
from django.urls import path,include
from car import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', views.signup, name='signup'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('enter-password/', views.enter_password, name='enter_password'),
    path('login/', views.LoginPage, name='login'),
    path('', views.HomePage, name='home'),
    path('logout/', views.LogoutPage, name='logout'),
    path('contact/', views.ContactPage, name='contact'),
    path('about/', views.AboutPage, name='about'),
    path('product/', views.ProductPage, name='product'),
    path('save_order/', views.save_order, name='save_order'),
    path('profile/',views.userprofile,name='profile'),
    path('order/',views.order,name='orders'),
    path('product_details/<int:product_id>/',views.product_details, name='product_details'),
    path("__debug__/", include("debug_toolbar.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
