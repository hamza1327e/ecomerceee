from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from car.models import Contact, Product, Category, Order, Clothing, Review, User_profile, Color, Size, User_Verification
from car.forms import ReviewForm
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.cache import cache
from django.db.models import Prefetch
from django.db.models import Sum, aggregates
import random
from django.core.mail import send_mail



def HomePage(request):
    products = Product.objects.prefetch_related(
        'category').select_related('clothing').all()
    data = {'products': products}
    return render(request, 'home.html', data)

def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass')
        user = authenticate(request, username=username, password=pass1)
        if user is not None:
            login(request, user)
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Username or password is incorrect!'})

    return render(request, 'login.html')


def LogoutPage(request):
    logout(request)
    return redirect('home')


def ContactPage(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        contact = Contact(name=name, email=email, message=message)
        contact.save()
        messages.success(
            request, "Thank You For Contacting Us, we will get back soon!")
    return render(request, 'contact.html')


def AboutPage(request):
    return render(request, 'about.html')


def ProductPage(request):
    products = Product.objects.select_related('clothing').all()
    data = {'products': products}
    return render(request, 'products.html', data)


def __str__(self):
    return self.name


def product_details(request, product_id):
    details = get_object_or_404(Clothing, id=product_id)
    similar_products = details.get_similar_products()
    if request.method == 'POST':
        parent_review_id = request.POST.get('parent_review')
        parent_review = None

        if parent_review_id:
            try:
                parent_review = Review.objects.get(id=parent_review_id)
            except Review.DoesNotExist:
                parent_review = None

        reviewform = ReviewForm(request.POST, parent_review=parent_review)

        if reviewform.is_valid():
            review = reviewform.save(commit=False)
            review.product = details
            review.user = request.user
            review.save()
            return redirect('product_details', product_id=product_id)
    else:
        reviewform = ReviewForm()

    reviews = details.reviews.filter(parent_review__isnull=True)

    data = {
        'details': details,
        'reviewform': reviewform,
        'reviews': reviews,
        'simp': similar_products
    }

    return render(request, 'product_details.html', data)


def save_order(request):
    if request.method == "POST":
        s_size_id = int(request.POST.get('size'))
        s_color_id = int(request.POST.get('color'))
        quantity = int(request.POST.get('quantity'))
        c_name = request.POST.get('name')
        city = request.POST.get('city')
        address = request.POST.get('address')
        number = int(request.POST.get('number'))
        p_id = int(request.POST.get('product_id'))

        product = get_object_or_404(Clothing, pk=p_id)
        color = get_object_or_404(Color, pk=s_color_id)
        size = get_object_or_404(Size, pk=s_size_id)

        order = Order(
            user=request.user,
            product=product,  # Pass the product object
            size=size,
            color=color,
            quantity=quantity,
            city=city,
            address=address,
            number=number,
            customer_name=c_name,
        )
        order.save()
        return redirect('product_details', product_id=p_id)

    # Fallback in case no POST request
    return render(request, 'product_details.html')


def userprofile(request):
    if request.method == 'POST':
        u_name = request.POST.get('uname')
        f_name = request.POST.get('fname')
        l_name = request.POST.get('lname')
        p_pic = request.FILES.get('ppic')
        if User.objects.filter(username=u_name).exclude(pk=request.user.pk).exists():
            messages.error(request, "this username is already exists")
            return redirect('profile_orders')
        user = request.user
        user.username = u_name
        user.first_name = f_name
        user.last_name = l_name
        user.save()
        profile = User_profile.objects.get(user=user)
        if p_pic:
            profile.image = p_pic
            profile.save()
            messages.success(
                request, 'Your profile has been updated successfully.')
        return redirect('profile')
    profile = User_profile.objects.get(user=request.user)
    context = {'profile': profile}
    return render(request, 'profile_orders.html', context)


@login_required
def order(request):
    user = request.user
    order = Order.objects.filter(user=user)
    total_price_sum = order.aggregate(Sum('total_price'))[
        'total_price__sum'] or 0
    context = {'order': order, 'total_price_sum': total_price_sum}
    return render(request, 'orders.html', context)


def generate_verification_code():
    return str(random.randint(100000, 999999))


def send_verification_email(email, code):
    send_mail(
        'Your Verification Code',
        f'Your verification code is {code}',
        'sherazhamza1411@gmail.com',
        [email],
        fail_silently=False,
    )


def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code = generate_verification_code()
        request.session['email'] = email
        request.session['code'] = code
        send_verification_email(email, code)
        User_Verification.objects.create(email=email, verficationcode=code)
        return redirect('verify_email')
    return render(request, 'signup.html')

def verify_email(request):
    if request.method == 'POST':
        email = request.session.get('email')
        entered_code = request.POST.get('code')

        try:
            verification = User_Verification.objects.get(
                email=email, verficationcode=entered_code
            )

            if verification.is_expired():
                verification.delete()
                messages.error(request, 'Verification code is expired. Please request a new code.')
                return redirect('signup')

            username = email.split('@')[0]
            request.session['username'] = username
            messages.success(request, 'Email verified successfully!')
            return redirect('enter_password')

        except User_Verification.DoesNotExist:
            messages.error(request, 'Your verification code is incorrect.')
            return redirect('verify_email')

    return render(request, 'verify.html')

def enter_password(request):
    email = request.session.get('email')

    if not email:
        return redirect('signup')  # Ensure email exists in the session

    if request.method == 'POST':
        password = request.POST.get('password')
        username = request.session.get('username')

        if not username:
            username = email.split('@')[0]  # Default username to email prefix

        # Create the user
        user, created = User.objects.get_or_create(
            username=username, email=email
        )

        if created:
            user.set_password(password)
            user.save()
            messages.success(request, "Account created successfully!")
        else:
            messages.warning(request, "User already exists. You are now logged in.")
            login(request, user)
            return redirect('home')  # Redirect to home if user exists

        # If the account was newly created, log them in
        login(request, user)
        messages.success(request, "You are now logged in!")
        return redirect('home')

    return render(request, 'password.html')
