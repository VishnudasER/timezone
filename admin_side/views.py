from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from cart.models import *
from django.http import HttpResponse
from .forms import CouponForm
from django.http import HttpResponseForbidden
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import textwrap
from reportlab.lib.pagesizes import A3
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors

from django.db.models import Q
from django.db.models import Sum
from django.db.models import Count

def superadmin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('error')
    return wrapper


@superadmin_required
@never_cache
def admin_dsh(request):
    if request.user.is_authenticated:
        ncustomer = User.objects.all().exclude(is_superuser=True).count()
        nproduct = Product.objects.all().count()
        norder = Order.objects.all().count()
        products = Product.objects.all()
        
        # Calculate top-selling brand
        top_selling_brand = OrderItem.objects.values('product__brand__title').annotate(total_sales=Sum('quantity')).order_by('-total_sales')[:1]
        top_selling_brands = OrderItem.objects.values('product__brand__title').annotate(total_sales=Sum('quantity')).order_by('-total_sales')[:10]
        top_selling_products = OrderItem.objects.values( 'product__title', 'product__category__title', 'product__brand__title', 'product__image1').annotate(total_quantity=Sum('quantity'), order_count=Count('order__id')).order_by('-total_quantity')[:10]
        # print(top_selling_products)
        # Calculate top-selling category
        top_selling_category = OrderItem.objects.values('product__category__title').annotate(total_sales=Sum('quantity')).order_by('-total_sales')[:1]
        top_selling_categoriess = OrderItem.objects.values('product__category__title').annotate(total_sales=Sum('quantity')).order_by('-total_sales')[:10]
        
        top_selling_products_data = OrderItem.objects.values('product__title').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:10]
        top_selling_products_labels = [item['product__title'] for item in top_selling_products_data]
        top_selling_products_quantities = [item['total_quantity'] for item in top_selling_products_data]
        total_orders = norder   
        total_sales = OrderItem.objects.filter(order__status='delivered').aggregate(total_sales=Sum('price'))['total_sales'] or 0
        
        category_sale = get_category_sales()

        return render(request, "admin-side/admin_dsh.html", {
            'ncustomer': ncustomer,
            'nproduct': nproduct,
            'norder': norder,
            'top_selling_brand': top_selling_brand,
            'top_selling_brands': top_selling_brands,
            'top_selling_category': top_selling_category,
            'top_selling_categoriess' : top_selling_categoriess,
            'top_selling_products': top_selling_products,
            'top_selling_products_data': {
                'labels': top_selling_products_labels,
                'quantities': top_selling_products_quantities,
            },
            'total_orders': total_orders,
            'total_sales': total_sales,
            'products' : products,
            'category_sale': category_sale
            
        })
    else:
        return redirect('home')
    

def get_category_sales():
    category_sales = {}
    categories = Category.objects.all()
    for category in categories:
        total_sales = OrderItem.objects.filter(product__category=category).aggregate(total_sale=Sum('price'))['total_sale']
        total_sales = total_sales if total_sales else 0
        category_sales[category.title] = total_sales
    return category_sales    


@superadmin_required
@never_cache
def show_category(request):
    if request.user.is_authenticated:
        category = Category.objects.all()
        return render(request,'admin-side/show_category.html',{'category':category})
    else:
        return redirect('home')

@superadmin_required
@never_cache
def add_category(request):
    if request.user.is_authenticated:
        return render(request,'admin-side/add_category.html')
    else:
        return redirect('home')


@superadmin_required
def add_category_action(request):
    if request.method == 'POST':
        new_category = request.POST.get('new_category')
        existing_category = Category.objects.filter(title=new_category)

        if existing_category.exists():
            messages.error(request, 'Category already exists')
            return redirect('add_category')
        else:
            category = Category(title=new_category)
            category.save()

    return redirect('show_category')


@superadmin_required
@never_cache
def edit_category(request,cid):
    if request.user.is_authenticated:
        category = Category.objects.get(id=cid)
        return render(request,'admin-side/edit_category.html', {'category':category})
    else:
        return redirect ('home')


@superadmin_required
def edt_category_action(request):
    if request.method== 'POST':
        id = request.POST.get('id')
        name = request.POST.get('newcategory')
        existing_category = Category.objects.filter(title=name)
        if existing_category.exists():
            messages.error(request, 'Category already exists')
            return redirect('add_category')
        else:
            category = Category.objects.get(id=id)
            category.title = name
            category.save()
            return redirect('show_category')


@superadmin_required
def delete_category(request,id):
    a=Category.objects.get(id=id)
    a.delete()
    return redirect('show_category')


@superadmin_required
@never_cache
def show_brand(request):
    if request.user.is_authenticated:
        brand = Brand.objects.all()
        return render(request,'admin-side/show_brand.html',{'brand':brand})
    else:
        return redirect('home')
    

@superadmin_required    
@never_cache
def add_brand(request):
    if request.user.is_authenticated:
        return render(request,'admin-side/add_brand.html')
    else:
        return redirect('home')


@superadmin_required
def add_brand_action(request):
    if request.method == 'POST':
        new_brand = request.POST.get('new_brand')
        existing_brand = Brand.objects.filter(title=new_brand)

        if existing_brand.exists():
            messages.error(request, 'Brand already exists')
            return redirect('add_brand')
        else:
            brand = Brand(title=new_brand)
            brand.save()
    return redirect('show_brand')



@superadmin_required
@never_cache
def edit_brand(request,bid):
    if request.user.is_authenticated:
        brand = Brand.objects.get(id=bid)
        return render(request,'admin-side/edit_brand.html', {'brand':brand})
    else:
        return redirect('home')


@superadmin_required
def edt_brand_action(request):
    if request.method== 'POST':
        id = request.POST.get('id')
        name = request.POST.get('editbrand')
        existing_brand = Brand.objects.filter(title=name)
        if existing_brand.exists():
            messages.error(request, 'Brand already exists')
            return redirect('edit_brand')
        else:
            brand = Brand.objects.get(id=id)
            brand.title = name
            brand.save()
            return redirect('show_brand')


@superadmin_required
def delete_brand(request,id):
    if request.user.is_authenticated:
        a=Brand.objects.get(id=id)
        a.delete()
    return redirect('show_brand')

    

@superadmin_required
@never_cache 
def show_product(request):
    if request.user.is_authenticated:
        products = Product.objects.all()
        return render(request,'admin-side/show_product.html',{'products':products})
    else:
        return redirect('home')


@superadmin_required
@never_cache
def admin_view_product(request,uid):
    if request.user.is_authenticated:
        products = Product.objects.get(id=uid)
        return render(request, 'admin-side/view_products.html',{'products':products})
    else:
        return redirect('home')


@superadmin_required
@never_cache
def admin_delete_product(request,id):
    if request.user.is_authenticated:
        products=Product.objects.get(id=id)
        products.delete()
        return redirect('show_product')
    else:
        return redirect('home')
    

@superadmin_required
@never_cache
def edit_product(request, uid):
    if request.user.is_authenticated:
        product = Product.objects.get(id=uid)
        category = Category.objects.all()
        brand = Brand.objects.all()
        return render(request,'admin-side/edit_product.html', {'product': product, 'category': category, 'brand':brand})
    else:
        return redirect('home')


@superadmin_required
def edit_product_action(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            id = request.POST.get('id')
            name = request.POST.get('name')

            # Check if a product with the same name already exists
            if Product.objects.exclude(id=id).filter(title=name).exists():
                messages.error(request, 'Product with this name already exists.')
                return redirect('edit_product', uid=id)

            description = request.POST.get('description')
            category = request.POST.get('category')
            brand = request.POST.get('brand')
            stock = request.POST.get('stock')
            price1 = request.POST.get('price1')
            price2 = request.POST.get('price2')
            img1 = request.FILES.get('img1')
            img2 = request.FILES.get('img2')
            img3 = request.FILES.get('img3')
            img4 = request.FILES.get('img4')

            product = Product.objects.get(id=id)

            product.title = name
            product.description = description
            product.stock = stock
            product.price = price1
            product.old_price = price2
            product.category_id = category
            product.brand_id = brand

            if img1 is not None:
                product.image1 = img1
            if img2 is not None:
                product.image2 = img2
            if img3 is not None:
                product.image3 = img3
            if img4 is not None:
                product.image4 = img4

            # Save the updated product
            product.save()
            return redirect('show_product')
        else:
            return redirect('show_product')
    else:
        return redirect('home')


@superadmin_required
@never_cache
def add_product(request):
    if request.user.is_authenticated:
        category = Category.objects.all()
        brand = Brand.objects.all()
        context = {
            'category':category,
            'brand':brand
        }
        return render(request,'admin-side/add_product.html',context)
    else:
        return redirect('home')


@superadmin_required
def add_product_action(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            name = request.POST.get('name')

            # Check if a product with the same name already exists
            if Product.objects.filter(title=name).exists():
                messages.error(request, 'Product with this name already exists.')
                return redirect('add_product')

            description = request.POST.get('description')
            brand = request.POST.get('brand')
            category = request.POST.get('category')
            stock = request.POST.get('stock')
            price = request.POST.get('price1')
            old_price = request.POST.get('price2')
            img1 = request.FILES.get('img1')
            img2 = request.FILES.get('img2')
            img3 = request.FILES.get('img3')
            img4 = request.FILES.get('img4')
            product = Product(title=name, brand_id=brand, category_id=category, price=price, old_price=old_price,
                              stock=stock, description=description, image1=img1, image2=img2, image3=img3, image4=img4)
            product.save()
            return redirect('show_product')
        else:
            return redirect('show_product')
    else:
        return redirect('home')

@superadmin_required
@never_cache
def show_user(request):
    if request.user.is_authenticated:
        users= User.objects.all().exclude(is_superuser=True)
        return render(request,'admin-side/show_user.html',{'users':users})
    else:
        return redirect('home')



@superadmin_required
def customeraction(request, uid):
    if request.user.is_authenticated:
        customer = User.objects.get(id=uid)
        if customer.is_active:
            customer.is_active = False
            print(customer.is_active)
        else:
            customer.is_active = True
        customer.save()
        return redirect('show_user')
    else:
        return redirect('home')

@superadmin_required
def product_action(request, uid):
    product = Product.objects.get(id=uid)
    if product.active:
        product.active = False
    else:
        product.active = True
    product.save()
    return redirect('show_product')


@superadmin_required
def category_action(request, cid):
    category = Category.objects.get(id=cid)
    if category.active:
        category.active = False
    else:
        category.active = True
    category.save()
    return redirect('show_category')


@superadmin_required
def brand_action(request, bid):
    brand = Brand.objects.get(id=bid)
    if brand.active:
        brand.active = False
    else:
        brand.active = True
    brand.save()
    return redirect('show_brand')
    


@superadmin_required

def customer_list(request):
    search_query = request.GET.get('search', '')
    
    if search_query:
        users = User.objects.filter(username__icontains=search_query) | User.objects.filter(email__icontains=search_query)
    else:
        users = User.objects.all().exclude(is_superuser=True)
    
    return render(request, 'admin-side/show_user.html', {'users': users, 'search_query': search_query})



@superadmin_required
def order(request):
    orders = Order.objects.all()
    return render(request, 'admin-side/admin_orderview.html', {'orders': orders, 'title': 'Order'})

@superadmin_required
def order_view(request,order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    order_status_choices = [
        (status, status_display) for status, status_display in Order.ORDER_STATUS_CHOICES if status != 'returned'
    ]
    context = {'title':'Order Details',
             'order':order,
             'order_items':order_items,
             'order_status_choices':order_status_choices}
    return render(request,'admin-side/order_view.html',context)



def order_update(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        if new_status:
            order.status = new_status
            
            if new_status == 'delivered' and order.billing_status=='COD':
                order.paid=True
                order.save()
                
            if (new_status == 'cancelled') and order.paid==True:
                order_items = OrderItem.objects.filter(order=order)
                for item in order_items:
                    item.product.Stock += item.quantity
                    item.product.save()

                Wallet.objects.create(user=order.user, amount=order.total_paid, order=order)

            order.save()
            return redirect('order_view', order_id=order_id)
    return render(request,'admin-side/order_view.html', {'order': order})



@superadmin_required
def order_return(request,order_id):
    order = get_object_or_404(Order,id=order_id)
    if request.POST.get('action') == 'approve':
        order.is_return_requested = False
        order.is_return_approved = True
        order.save()
    elif request.POST.get('action')=='reject':
        order.is_return_requested=False
        order.save()
    return redirect('order',order_id=order.id)



@superadmin_required
def returnedorders(request):
    returned = Returnedproduct.objects.all()
    return render(request,'admin-side/returnedorders.html',{'returned':returned,'title':'Returned Orders'})
    
    

@superadmin_required
def returned_details(request, id):
    returned = Returnedproduct.objects.get(id=id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            returned.return_status = new_status
            order = returned.order
            if new_status == returned.RETURNED:
                order.status = order.RETURNED
                order.save()
                
            order_items = OrderItem.objects.filter(order=order)
            for item in order_items:
                item.product.stock += item.quantity
                item.product.save()
            amount = order.total_paid if order.total_paid is not None else 0
            Wallet.objects.create(user=order.user, amount=order.total_paid or 0, order=order)
            returned.save()
            
            return redirect('returned_details', id=id)
    return render(request, "admin-side/return_view.html", {'returned':returned,'title':'Returned Order Details'})



def error(request):
    return render(request,'admin-side/404.html')


def coupon(request):
    coupon =Coupon.objects.all()
    return render(request,'admin-side/admincoupon.html' ,{'coupon':coupon,'title':'Coupon'})


def addcoupon(request):
    if request.method == 'POST':
        code =request.POST.get('coupon-code')
        expiry_date =request.POST.get('expiry_date')
        discount_price =request.POST.get('discount_price')
                     
        Coupon.objects.create(coupon_code=code,is_expired =expiry_date,discount_price=discount_price)
        
        return redirect('coupon')
    else:
        return redirect('coupun')


def edit_coupon(request,id):
    coupon =Coupon.objects.get(id=id)
    return render(request,'admin-side/edit_coupon.html',{'coupon':coupon,'title':'Edit Coupon'})

def edit_couponaction(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        code = request.POST.get('code')
        expiry_date = request.POST.get('expiry_date')
        discount_price = request.POST.get('discount_price')
        
        coupon=Coupon.objects.get(id=id)
        
        coupon.coupon_code = code
        coupon.is_expired = expiry_date
        coupon.discount_price = discount_price
        coupon.save()
        return redirect('coupon')

    return render(request,'admin-side/admincoupon.html')


def delete_coupon(request, id):
    try:
        coupon = Coupon.objects.get(id=id)
        coupon.delete()
        return redirect('coupon')
    except Coupon.DoesNotExist:
        # Handle the case where the coupon does not exist
        return redirect('coupon')

def category_Offer(request):
    categoryoffer =CategoryOffer.objects.all()
    category=Category.objects.exclude(active=False)
    return render(request,'admin-side/admin_categoryoffer.html',{'title':'Category Offer','categoryoffer':categoryoffer,'category':category})

def add_category_Offer(request):
    category=Category.objects.exclude(active=False)
    if request.method == 'POST':
        category = request.POST.get('category')
        percent_offer = request.POST.get('percent_offer')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        CategoryOffer.objects.create(
            category_id=category,
            percent_offer=percent_offer,
            start_date=start_date,
            end_date=end_date
        )
        return redirect('category_Offer')
    else:
        return render(request,'admin-side/admin_categoryoffer.html',{'category':category})


def edit_category_offer(request, offer_id):
    category_offer = get_object_or_404(CategoryOffer, id=offer_id)
    categories = Category.objects.exclude(active=False)

    if request.method == 'POST':
        category = request.POST.get('category')
        percent_offer = request.POST.get('percent_offer')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        category_offer.category_id = category
        category_offer.percent_offer = percent_offer
        category_offer.start_date = start_date
        category_offer.end_date = end_date
        category_offer.save()

        return redirect('category_Offer')
    else:
        return render(request, 'admin-side/edit_category_offer.html', {'category_offer': category_offer, 'categories': categories})

def delete_category_Offer(request,offer_id):
    category_offer = get_object_or_404(CategoryOffer, id=offer_id)
    category_offer.delete()
    return redirect('category_Offer')

# product Offer

def product_Offer(request):
    productoffer =ProductOffer.objects.all()
    product=Product.objects.exclude(active=False)
    return render(request,'admin-side/admin_productoffer.html',{'title':'Product Offer','productoffer':productoffer,'product':product})

def add_product_Offer(request):
    product=Product.objects.exclude(active=False)
    if request.method == 'POST':
        product = request.POST.get('product')
        percent_offer = request.POST.get('percent_offer')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        ProductOffer.objects.create(
            product_id=product,
            percent_offer=percent_offer,
            start_date=start_date,
            end_date=end_date
        )
        return redirect('product_Offer')
    else:
        return render(request,'admin-side/admin_productoffer.html',{'product':product})


def edit_product_offer(request, offer_id):
    product_offer = get_object_or_404(ProductOffer, id=offer_id)
    product = Product.objects.exclude(active=False)

    if request.method == 'POST':
        product = request.POST.get('product')
        percent_offer = request.POST.get('percent_offer')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        product_offer.product_id = product
        product_offer.percent_offer = percent_offer
        product_offer.start_date = start_date
        product_offer.end_date = end_date
        product_offer.save()

        return redirect('product_Offer')
    else:
        return render(request, 'admin-side/edit_product_offer.html', {'title':'Edit Product Offer','product_Offer': product_offer, 'product': product})

def delete_product_Offer(request,offer_id):
    product_Offer = get_object_or_404(ProductOffer, id=offer_id)
    product_Offer.delete()
    return redirect('product_Offer')


from django.db.models import Sum
from decimal import Decimal
from django.db.models import Sum, F



@never_cache
def salesreport(request):
    # Exclude orders with total paid as None
    orders = Order.objects.filter(status='delivered').exclude(total_paid=None)

    total_sales = orders.aggregate(total_paid_sum=Sum('total_paid'))['total_paid_sum'] or Decimal(0)
    order_items = OrderItem.objects.filter(order__in=orders)
    item_quantity_sold = sum(item.quantity for item in order_items)

    # Calculate total discount, handling possible None values
    total_discount = sum((item.price - (item.order.total_paid or Decimal(0))) for item in order_items)

    # Add the total discount from the checkout function
    total_cart_price = Decimal(request.session.get('total_cart_price', '0.00'))
    total_paid = Decimal(request.session.get('total_paid', '0.00'))

    total_discount += total_cart_price - total_paid  # Adjust the total discount calculation

    # Fetch applied coupon for the current user
    user = request.user
    applied_coupon = Applied_coupon.objects.filter(user=user, applied=True).first()

    # Apply coupon discount if it exists
    if applied_coupon:
        coupon_discount = applied_coupon.coupon.discount_price
        total_discount += coupon_discount

    if request.method == 'POST' and 'generate_pdf' in request.POST:
        pdf = generate_sales_report_pdf(orders, total_sales, order_items, item_quantity_sold)

        response = HttpResponse(content_type='application/pdf')
        d = timezone.now().strftime('%y-%m-%d')
        response['Content-Disposition'] = f'inline; filename="{d}_sales_report.pdf"'
        response.write(pdf)
        return response

    # Add discount per product to each order item
    for item in order_items:
        item.discount = item.price - (item.order.total_paid or Decimal(0))

    context = {
        'title': 'Sales Report',
        'order': orders,
        'total_sales': total_sales,
        'order_items': order_items,
        'item_quantity_sold': item_quantity_sold,
        'total_discount': total_discount,
        'applied_coupon': applied_coupon,
    }

    return render(request, 'admin-side/admin_salesreport.html', context)




def filter_salesreport(request):

    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        
        if start_date and end_date:
            try:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

                if end_date < start_date:
                    messages.error(request, "End date should be greater than or equal to the Start date.")
                    return redirect('salesreport')

                orders = Order.objects.filter(
                    Q(created__date__gte=start_date) & Q(created__date__lte=end_date),
                    status='delivered'
                )
                order_items = OrderItem.objects.filter(order__in=orders)
                print("jskjskdjskdjksjdkfjkfjksjfkjfsk")
                # Calculate total sales, quantity sold, and total discount
                total_sales = orders.aggregate(Sum('total_paid'))['total_paid__sum'] or 0
                item_quantity_sold = order_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
                total_discount = sum(item.price - item.order.total_paid for item in order_items)

                context = {
                    'title': 'Sales Report',
                    'orders': orders,
                    'order_items': order_items,
                    'start_date': start_date,
                    'end_date': end_date,
                    'total_sales': total_sales,
                    'item_quantity_sold': item_quantity_sold,
                    'total_discount': total_discount,
                }

                return render(request, 'admin-side/admin_salesreport.html', context)

            except ValueError:
                messages.error(request, "Invalid Date")
                return redirect('salesreport')

    return redirect('salesreport')



def generate_sales_report_pdf(orders, total_sales, order_items, item_quantity_sold, start_date=None, end_date=None):
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A3)

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
    title_text = f"Sales Report - {timezone.now().strftime('%Y-%m-%d')}"
    content.append(Paragraph(title_text, title_style))

    # Table headers and data
    table_data = [
        ["Order ID", "Customer", "Total Paid", "Status", "Product", "Price", "Quantity Sold", "Date"]
    ]

    # Populate table data
    for order in orders:
        for item in order.items.all():
            # Wrap product name and date after 20 characters
            wrapped_product_name = textwrap.fill(item.product.title, width=20)
            wrapped_date = textwrap.fill(str(order.created), width=20)

            row_data = [
                str(order.id),
                str(order.user.username),
                f"${order.total_paid}",
                str(order.status),
                f"{wrapped_product_name}\n",  # Product name on a new line
                f"${item.price}",
                str(item.quantity),
                f"{wrapped_date}\n",  # Date on a new line
            ]
            table_data.append(row_data)

    # Adjust column widths for A3
    col_widths = [50, 100, 80, 60, 120, 50, 80, 100]

    # Create a table with styles
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Add table to content
    content.append(table)

    # Save the PDF
    pdf.build(content)

    pdf_output = buffer.getvalue()
    buffer.close()
    return pdf_output

