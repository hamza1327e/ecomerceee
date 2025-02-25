from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta


# Category model definition
class Category(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Size(models.Model):
    sizes = models.CharField(max_length=50)


class Color(models.Model):
    color = models.CharField(max_length=50)
    image = models.ImageField(upload_to='uploads/colors/')


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Product(TimeStampedModel):
    name = models.CharField(max_length=50)
    price = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.CharField(
        max_length=200, default='', null=True, blank=True)
    image = models.ImageField(upload_to='uploads/products/')
    stock = models.IntegerField(default=0)
    sales = models.IntegerField(default=0)

    def get_similar_products(self):
        return Product.objects.annotate(
            similarity=TrigramSimilarity('name', self.name)
        ).filter(
            Q(category=self.category) & ~Q(id=self.id) & Q(similarity__gt=0.3)
        ).order_by('-similarity')[:5]

    def is_in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-updated_at',)


class User_profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='uploads/profile/', default='uploads/profile/default.jpg')

    def __str__(self):
        return self.user.username


class Clothing(Product):
    sizes = models.ManyToManyField(Size)
    colors = models.ManyToManyField(Color)
    material = models.CharField(max_length=255)
    gender = models.CharField(max_length=50, choices=[
                              ('Male', 'M'), ('Female', 'F')])
    brand = models.CharField(max_length=255)


class Review(TimeStampedModel):
    product = models.ForeignKey(
        Clothing, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(null=True, blank=True)
    comment = models.TextField()
    parent_review = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f'reply by {self.user.username}'


# Order model inheriting the timestamp fields
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='orders')
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    customer_name = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    number = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.IntegerField(editable=False)
    status = models.CharField(
        max_length=50,
        choices=[('pending', 'Pending'), ('shipped', 'Shipped'),
                 ('delivered', 'Delivered')],
        default='pending'  # Set default value to 'pending'
    )

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order for {self.product.name} by {self.customer_name}"

    class Meta:
        ordering = ('-created_at',)

# Contact model inheriting the timestamp fields


class Contact(TimeStampedModel):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    message = models.TextField()

    def __str__(self):
        return f'Message from {self.name} ({self.email})'

    class Meta:
        ordering = ('-created_at',)


class User_Verification(models.Model):
    email = models.EmailField(unique=True)
    verficationcode = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)
