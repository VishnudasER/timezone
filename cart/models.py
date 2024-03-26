from django.db import models
from django.contrib.auth.models import User
from admin_side.models import *
from django.conf import settings
from user.models import *
import uuid
# Create your models here.
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return str(self.product.title)

    def discounted_price(self):
        return self.product.get_discounted_price()

    def total_price(self):
        # Use discounted_price instead of product.price
        return self.quantity * self.discounted_price()

    class Meta:
        db_table = 'cart'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name='order_user', null=True,blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    billing_status = models.CharField(max_length=10,default=total_paid )
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True,blank=True)
    active = models.BooleanField(default=True)
    paid = models.BooleanField(default=False)
    
    # New field for order status
    RETURNED ='returned'
    CANCEL = 'cancelled'
    ORDER_STATUS_CHOICES = [
        ('confirmed', 'Order Confirmed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled','cancelled'),
        ('returned','returned'),

    ]

    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='confirmed')

    class Meta:
        ordering = ('-created',)
        db_table='Orders'

    def str(self):
        return f"{self.created} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order,related_name='items',on_delete=models.CASCADE,blank=True,null=True)
    product = models.ForeignKey(Product,related_name='order_items',on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return str(self.id)

    class MaxValidator:
        pass
    
    

class Returnedproduct(models.Model):
    RETURN_PENDING = 'Return Pending'
    RETURNED = 'Returned'
    REJECTED = 'Rejected'

    RETURN_STATUS_CHOICES = (
        (RETURN_PENDING, 'Return Pending'),
        (RETURNED, 'Returned'),
        (REJECTED, 'Rejected')
    )

    order = models.ForeignKey(Order, related_name='returned_products', on_delete=models.CASCADE)
    reason = models.TextField()
    return_status = models.CharField(max_length=20, choices=RETURN_STATUS_CHOICES, default=RETURN_PENDING)
    returned_at = models.DateTimeField(auto_now_add=True)
    received_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.order.id} - {self.return_status}"

    def calculate_returned_amount(self):
        # Calculate the total returned amount for this returned product
        returned_items = ReturnedItem.objects.filter(returned_product=self)
        total_returned_amount = sum(item.price for item in returned_items)
        return total_returned_amount


class ReturnedItem(models.Model):
    returned_product = models.ForeignKey(Returnedproduct, on_delete=models.CASCADE, related_name='returned_items')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)  # Assuming you have an OrderItem model

    def __str__(self):
        return f"ReturnedItem {self.id} for OrderItem {self.order_item.id}"
    

class Wallet(models.Model):
    DEBIT = 'Debit'
    CREDIT = 'Credit'

    BALANCE_TYPE = (
        (DEBIT, 'Debit'),
        (CREDIT, 'Credit')
    )
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order =models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance_type = models.CharField(max_length=15, choices=BALANCE_TYPE, default=CREDIT)
    balance_returned = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.username}'s Wallet"

    def total_balance(self):
        balance = 0
        if self.balance_type == Wallet.DEBIT:
            balance -= self.amount
        else:
            balance += self.amount
        return balance
    