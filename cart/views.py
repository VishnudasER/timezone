from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product, CartItem, Wishlist, Order, OrderItem, Returnedproduct,Wallet
from user.models import *
from decimal import Decimal
from django.views.decorators.cache import never_cache
from admin_side.models import *
from admin_side.forms import *
from datetime import datetime
from django.http import HttpResponse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.urls import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum,  Case, When, F, DecimalField
from io import BytesIO
import textwrap
from django.utils import timezone
from django.http import HttpResponse
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A3
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors


@never_cache
@login_required(login_url='login_perform')
def add_to_cart(request, uid):
    if not request.user.is_authenticated:
        messages.warning(request, 'You need to sign in first.')
        return redirect('login_perform')

    product = get_object_or_404(Product, id=uid)
    if product.stock == 0:
        messages.error(request, f"{product.title} is out of stock.")
    elif CartItem.objects.filter(product=product, user=request.user).exists():
        messages.error(request, f"{product.title} already exists in the cart.")
    else:
        item = CartItem.objects.create(
            product=product,
            user=request.user,
            quantity=1,
        )
        messages.success(request, f"{item.product.title} added to the cart successfully!")

    # Remove product from wishlist if it exists
    if Wishlist.objects.filter(user=request.user, product=product).exists():
        Wishlist.objects.filter(user=request.user, product=product).delete()
        messages.info(request, f"{product.title} removed from your wishlist as it's added to the cart.")

    default_url = '/'
    referer = request.META.get('HTTP_REFERER', default_url)

    try:
        return redirect(referer)
    except ValueError:
        messages.error(request, 'Invalid URL for redirection. Please try again.')
        return redirect(default_url)
    
    
@never_cache
@login_required(login_url='login_perform')
def cart(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        total_cart_price = float(sum(item.total_price() for item in cart_items))

        return render(request, 'user/cart.html', {'cart_items': cart_items, 'total_cart_price': total_cart_price})
    else:
        return redirect('login_perform')



    
@login_required(login_url='login_perform')
def remove_cart_item(request, id):
    cart_item = get_object_or_404(CartItem, id=id, user=request.user)
    cart_item.delete()
    messages.success(request, 'The product has been removed from your cart.')
    return redirect('cart')


@login_required(login_url='login_perform')
def update_cart(request, id, action):
    cart_items = CartItem.objects.filter(product=id)

    for cart_item in cart_items:
        if action == 'increment':
            cart_item.quantity += 1
        elif action == 'decrement':
            cart_item.quantity -= 1

        # Ensure quantity is not negative
        cart_item.quantity = max(0, cart_item.quantity)

        if cart_item.quantity == 0:
            print('cart delete')
            cart_item.delete()
        else:
            cart_item.save()

    default_url = '/'
    referer = request.META.get('HTTP_REFERER', default_url)

    try:
        return redirect(referer)
    except ValueError:
        return redirect(default_url)
    
@login_required(login_url='login_perform')
def update_quantity(request, cart_item_id, action):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    if action == 'increment':
        # Increment the quantity
        if cart_item.quantity < 10 and cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
        elif cart_item.quantity >= 10:
            messages.error(request, 'Maximum quantity per product is 10.')
        elif cart_item.quantity >= cart_item.product.stock:
            messages.error(request, 'Cart amount exceeds stock of the product.')
    elif action == 'decrement':
        # Decrement the quantity (avoid going below 1)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            messages.error(request, 'At least 1 quantity should be in the cart.')
    else:
        return JsonResponse({'error': 'Invalid action'})

    # Save changes
    cart_item.save()

    # Recalculate the total price for the cart item
    total_price = cart_item.total_price()

    return JsonResponse({'success': True, 'total_price': total_price, 'quantity': cart_item.quantity})

@login_required(login_url='login_perform')
def checkout(request):
    # Fetch user's cart items
    cart_items = CartItem.objects.filter(user=request.user)

    # Recalculate total cart price based on the updated quantity
    total_cart_price = sum(item.total_price() for item in cart_items)

    # Fetch user addresses
    user_addresses = Address.objects.filter(user=request.user)

    # Calculate discount, shipping charge, and estimated tax based on your logic
    discount_amount = Decimal('0.01') * total_cart_price  # 1% discount
    shipping_charge = Decimal('0.005') * total_cart_price  # 0.5% shipping charge
    estimated_tax = Decimal('0.02') * total_cart_price  # 2% estimated tax

    # Calculate the new price after applying discounts, charges, and tax
    new_price = total_cart_price - discount_amount + shipping_charge + estimated_tax
    request.session['new_price'] = str(new_price)  # Convert Decimal to string before saving

    # Handle coupon form submission
    if request.method == 'POST':
        coupon_form = CouponForm(request.POST)
        if coupon_form.is_valid():
            code = coupon_form.cleaned_data['code']
            if Applied_coupon.objects.filter(user=request.user, coupon=code).exists():
                messages.error(request, f"The Coupon {code} is Already used before")
            else:
                try:
                    current_time = datetime.now()
                    coupon = Coupon.objects.get(coupon_code=code, is_expired__gte=current_time, active=True)
                    discounted_price = new_price - coupon.discount_price
                    
                    if discounted_price >= 0:
                        new_price = discounted_price
                        request.session['coupon'] = code
                        request.session['discount_price'] = str(coupon.discount_price)  # Convert Decimal to string
                        request.session['new_price'] = str(new_price)  # Convert Decimal to string
                        messages.success(request, f'Coupon {code} applied successfully!')
                    else:
                        messages.error(request, f"The coupon {code} cannot reduce the total below zero.")
                except Coupon.DoesNotExist:
                    messages.error(request, 'Invalid coupon code.')

    # Ensure there is at least one address for the user
    # if not user_addresses.exists():
    #     messages.warning(request, 'Please add an address before proceeding to checkout.')
    #     return redirect('add_address')

    # Check for out of stock or inactive products in the cart
    for cart_item in cart_items:
        if cart_item.quantity > cart_item.product.stock or not cart_item.product.active:
            messages.error(request, f'{cart_item.product.title} is out of stock or inactive.')
            return redirect('cart')

    # Pass the first address to the template as the default shipping address
    default_address = user_addresses.first()

    # Fetch user's wallet balance
    wallet_balance = Wallet.objects.filter(user=request.user).aggregate(total_balance=Sum(
        Case(
            When(balance_type=Wallet.DEBIT, then=F('amount') * -1),
            default=F('amount'),
            output_field=DecimalField()
        )
    ))['total_balance'] or Decimal('0.00')

    # Prepare context for rendering the checkout template
    context = {
        'cart_items': cart_items,
        'user_addresses': user_addresses,
        'total_cart_price': total_cart_price,
        'discount_amount': discount_amount,
        'shipping_charge': shipping_charge,
        'estimated_tax': estimated_tax,
        'default_address': default_address,
        'new_price': new_price,
        'wallet_balance': wallet_balance,
        'coupon_form': CouponForm()  
    }

    return render(request, 'user/checkout.html', context)


@login_required(login_url='login_perform')
def wishlist(request):
    wish = Wishlist.objects.filter(user=request.user)
    return render(request,'user/wishlist.html',{'wish':wish})

@login_required(login_url='login_perform')
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    wishlist_item, created = Wishlist.objects.get_or_create(product=product, user=request.user)

    if not created:
        messages.info(request, f"{product.title} already exists in the wishlist.")
    
    try:
        return redirect(wishlist)
    except ValueError:
        return redirect(cart)
    
    
@login_required(login_url='login_perform')
def wish_remove(request,id):
    wishlist_item =Wishlist.objects.get(id=id)
    if request.user.is_authenticated and wishlist_item.user == request.user:
        wishlist_item.delete()
        messages.success(request, "Item removed from wishlist.")
    else:
        messages.error(request, "You don't have permission to remove this item from the wishlist.")
    return redirect('wishlist')

@login_required(login_url='login_perform')
def order_success(request):
    return render(request,'user/ordersuccess.html')


@login_required(login_url='login_perform')
def place_order(request):
    cart = CartItem.objects.filter(user=request.user)
    new_price = request.session.get('new_price')
    total_price = request.session.get('total_price')
    discount_price = request.session.get('discount_price', 0)
    host = request.get_host()

    if not cart:
        messages.error(request, 'Your cart is empty. Please add items before placing an order.')
        return redirect('cart')

    for cart_item in cart:
        if cart_item.quantity > cart_item.product.stock or not cart_item.product.active:
            messages.error(request, f'{cart_item.product.title} is out of stock or inactive.')
            return redirect('cart')

    if request.method == 'POST':
        address = request.POST.get('address')
        payment_method = request.POST.get('paymentmethod')
        if not address:
            messages.error(request, 'Add an address before checkout.')
            return redirect('checkout')
        
        address = Address.objects.get(id=address)
        
        
        if payment_method == 'COD':
            if float(new_price) > 10000:
                messages.error(request, 'Orders above $10000 are not allowed cash on delivery.')
                return redirect('checkout')
            else:
                order = Order.objects.create(
                    user=request.user,
                    address=address,
                    total_paid=new_price,
                    billing_status=payment_method,
                )
                print('order', order)
                print('orderadd', order.address)

                for item in cart:
                    product = item.product
                    quantity = item.quantity
                    price = item.product.price * quantity

                    OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity)
                    product.stock -= item.quantity
                    product.save()

                cart.delete()
                return render(request, 'user/ordersuccess.html', {'order_id': order.id})

        elif payment_method == 'Wallet':
            user = request.user
            wallets = Wallet.objects.filter(user=user)
            wallet_balance = float(sum(wallet.total_balance() for wallet in wallets))

            if wallet_balance > float(new_price):
                coupon = request.session.get('coupon')
                order = Order.objects.create(user=user, address=address, total_paid=new_price,
                                             billing_status=payment_method, paid=True)
                Applied_coupon.objects.create(user=user, coupon=coupon)
                amount = order.total_paid if order.total_paid is not None else 0
                Wallet.objects.create(user=user, amount=order.total_paid, balance_type=Wallet.DEBIT)

                for item in cart:
                    product = item.product
                    quantity = item.quantity
                    price = item.product.price * quantity

                    OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity)
                    product.stock -= item.quantity
                    product.save()

                cart.delete()
                return render(request, 'user/ordersuccess.html', {'order_id': order.id})

            else:
                messages.error(request, 'Wallet does not have enough funds.')
                return redirect('checkout')

        else:
            items = []
            for item in cart:
                product = item.product
                quantity = item.quantity
                price = item.product.price * quantity

                item_dict = {
                    'product': product,
                    'quantity': quantity,
                    'price': price,
                    'discount_price': discount_price,

                }

                items.append(item_dict)

            paypal_checkout = {
                "business": settings.PAYPAL_RECEIVER_EMAIL,
                "amount": new_price,
                "currency_code": "USD",
                "item_name": items,
                "invoice": uuid.uuid4(),
                'notify_url': 'https://{}{}'.format(host, reverse('paypal-ipn')),
                'return_url': 'http://{}{}'.format(host, reverse('paymentsuccessful', kwargs={'address': address.id})),
                'cancel_return': 'http://{}{}'.format(host, reverse('paymentfailed')),

            }

            paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)
            context = {'paypal_payment': paypal_payment}
            return render(request, "user/success.html", context)

    else:
        print('Not placed')
        return redirect('checkout')


def paymentfailed(request):
    return HttpResponse("Payment failed or canceled. Please try again.")


@login_required(login_url='login_perform')
def order_listing(request):
    order = Order.objects.filter(user=request.user)
    product = Product.objects.filter(order__in=order)
    return render(request, 'user/order_listing.html', {'order': order,'product' : product})


@login_required(login_url='login_perform')
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.active:
        # Update stock quantities before changing the order status
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            item.product.stock += item.quantity
            item.product.save()

        # Change order status and set it to cancelled
        order.active = False
        order.status = 'cancelled'
        order.save()

    return redirect('order_listing')

def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    existing_return = Returnedproduct.objects.filter(order=order).first()

    if request.method == 'POST' and not existing_return:
        reason = request.POST.get('reason')

        # Create a Returnedproduct entry
        returned_product = Returnedproduct.objects.create(order=order, reason=reason)

        # Update the wallet for the returned amount
        wallet_amount = returned_product.calculate_returned_amount()
        Wallet.objects.create(user=order.user, amount=wallet_amount, balance_type=Wallet.CREDIT)

        messages.success(request, 'Return requested successfully.')
        return redirect('order_listing')

    if existing_return and existing_return.return_status == Returnedproduct.RETURNED:
        order_items = OrderItem.objects.filter(order=order)

        for item in order_items:
            item.product.stock += item.quantity
            item.product.save()

    return render(request, 'user/returnorder.html', {'order': order, 'existing_return': existing_return})


@login_required(login_url='login_perform')
def order_detailview(request, id):
    # Retrieve the order object based on the provided id
    order = Order.objects.get(id=id)
    order_name = get_object_or_404(Order, id=id)
    selected_address = order.address
    user_addresses = Address.objects.filter(user=request.user)

    total_order_price = sum(item.price * item.quantity for item in order.items.all())

    # Calculate discount, shipping charge, and estimated tax based on your logic
    discount_amount = Decimal('0.01') * total_order_price  # 1% discount
    shipping_charge = Decimal('0.005') * total_order_price  # 0.5% shipping charge
    estimated_tax = Decimal('0.02') * total_order_price  # 2% estimated tax
    new_price = total_order_price - discount_amount + shipping_charge + estimated_tax
    
    print('selected address',selected_address)

    return render(request, 'user/trackorder.html', {
        'order': order,
        'order_name': order_name,    
        'user_addresses': user_addresses, 
        'selected_address': selected_address,
        'discount_amount': discount_amount,
        'shipping_charge': shipping_charge,
        'estimated_tax': estimated_tax,
        'new_price': new_price,
    })

@login_required
def wallet(request):
    wallet = Wallet.objects.filter(user=request.user)
    total_balance = sum(wallet.total_balance() for wallet in wallet)
    return render(request, 'user/wallet.html', {'wallet': wallet, 'total_balance':total_balance})

def paymentsuccessful(request,address):
    print("sfsdfdgdgdfghdfhdfhdfhfcgbcbhcvbbb")
    user_address=Address.objects.get(id=address)
    cart =CartItem.objects.filter(user=request.user)
    total_cart_price = sum(item.total_price() for item in cart)
    coupon = request.session.get('coupon')
    Applied_coupon.objects.create(user=request.user, coupon=coupon)
    
    order = Order.objects.create(
            user=request.user,
            address=user_address,
            total_paid=total_cart_price,
            billing_status='paypal',
            paid=True
            )
    for item in cart:
        product = item.product
        quantity = item.quantity
        price = item.product.price * quantity

        OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity)
        x= item.quantity 
        product.stock -= x
        product.save()
    cart.delete()
    
    return render(request,'user/ordersuccess.html', {'order_id': order.id})


def base2(request):
    return render(request,'admin/base2.html')

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Order

def generate_invoice_pdf(order, selected_address, current_date):
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    # Content container for the PDF
    content = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        spaceAfter=12,
    )

    # Title
    title_text = f"Invoice - {order.id}"
    content.append(Paragraph(title_text, title_style))

    # Order Details
    order_details = [
        ["Product", "Price", "Quantity", "Total"]
    ]
    for item in order.items.all():
        # Calculate total price for each item
        total_price = item.price * item.quantity
        row_data = [
            item.product.title,
            f"${item.price}",
            str(item.quantity),
            f"${total_price}"  # Use calculated total price
        ]
        order_details.append(row_data)

    # Create a table for order details
    table = Table(order_details)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    content.append(table)

    # Selected Address, Total Price, Order Date, Invoice Date
    selected_address_info = [
        ["Name:", f"{selected_address.first_name} {selected_address.last_name}"],
        ["Address:", selected_address.address],
        ["Address 1:", selected_address.address],
        ["City:", selected_address.city],
        ["Zipcode:", selected_address.zipcode],
        ["Phone:", selected_address.phone],
    ]
    address_table = Table(selected_address_info)
    content.append(address_table)

    total_price_paragraph = Paragraph(f"<strong>Total Price:</strong> ${order.total_paid}", styles['Normal'])
    order_date_paragraph = Paragraph(f"<strong>Order Date:</strong> {order.created}", styles['Normal'])
    invoice_date_paragraph = Paragraph(f"<strong>Invoice Date:</strong> {current_date}", styles['Normal'])
    content.extend([total_price_paragraph, order_date_paragraph, invoice_date_paragraph])

    # Build PDF
    pdf.build(content)

    # Get PDF content from buffer
    pdf_output = buffer.getvalue()
    buffer.close()

    return pdf_output

def download_invoice(request, id):
    # Retrieve the order object based on the provided id
    order = get_object_or_404(Order, id=id, user=request.user)

    # Calculate total price for each item
    for item in order.items.all():
        item.total_price = item.price * item.quantity

    # Get the selected address
    selected_address = order.address

    # Generate PDF content for the invoice
    current_date = timezone.now().strftime('%Y-%m-%d')
    pdf_content = generate_invoice_pdf(order, selected_address, current_date)

    # Create HTTP response with PDF as attachment
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
    return response
