from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Category (models.Model):
    title = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Brand (models.Model):
    title = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    

class Product(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    image1 = models.ImageField(upload_to='prodents')
    image2 = models.ImageField(upload_to='prodents')
    image3 = models.ImageField(upload_to='prodents')
    image4 = models.ImageField(upload_to='prodents')
    active = models.BooleanField(default=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    old_price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.title
    
     
    def get_discounted_price(self):
        current_date = timezone.now().date()

        category_offer = CategoryOffer.objects.filter(
            category=self.category,
            start_date__lte=current_date,
            end_date__gte=current_date
        ).first()

        # Fetch product-level offer for this specific product
        product_offer = ProductOffer.objects.filter(
            product=self,
            start_date__lte=current_date,
            end_date__gte=current_date
        ).first()

        if category_offer and product_offer:
            # Check if the product-level offer is better than the category offer
            if product_offer.percent_offer > category_offer.percent_offer:
                return self.price - (self.price * product_offer.percent_offer / 100)
            else:
                return self.price - (self.price * category_offer.percent_offer / 100)
        elif category_offer:
            return self.price - (self.price * category_offer.percent_offer / 100)
        elif product_offer:
            return self.price - (self.price * product_offer.percent_offer / 100)
        else:
            return self.price 



class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField(default=1)
    
    
    

class Coupon(models.Model):
    coupon_code=models.CharField(max_length=100,unique=True)
    is_expired=  models.DateField(null=True)
    discount_price=models.IntegerField(default=100)
    minimum_amount=models.IntegerField(default=500)
    active =models.BooleanField(default=True)
    
    def __str__(self):
        return self.coupon_code

    
 
class Applied_coupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    coupon = models.CharField(max_length=50, null=True, blank=True)
    applied = models.BooleanField(default=True)
 
 
class ProductOffer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    percent_offer = models.DecimalField(max_digits=5, decimal_places=2) 
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Offer for {self.product.title} - {self.percent_offer}%"
        
class CategoryOffer(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    percent_offer = models.DecimalField(max_digits=5, decimal_places=2)  
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    
    def __str__(self):
        return f"Offer for {self.category.name} - {self.percent_offer}%"
    

class Banners(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='banners/')

    def __str__(self):
        return self.title