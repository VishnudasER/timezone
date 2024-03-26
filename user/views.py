from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import datetime
from django.views.decorators.cache import never_cache
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from admin_side.models import *
import pyotp
from datetime import datetime, timedelta
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from user.models import *
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password




def vishnu(request):
    return render(request,'user/base.html')


@never_cache
def home(request):
    product = Product.objects.all()
    return render(request,"user/home.html",{'product':product})


def sign_up(request):
    try:
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return render(request, 'user/usersignup.html')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return redirect('home')


def signup_perform(request):
    try:
        if request.method == 'POST':
            email = request.POST['email']
            username = request.POST['username']
            password_1 = request.POST['password_1']
            password_2 = request.POST['password_2']
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return redirect('sign_up')
            elif User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return redirect('sign_up')
            else:
                if password_1 == password_2:
                    request.session['mail'] = email
                    request.session['user_data'] = {
                        'username': username,
                        'email': email,
                        'password': password_1
                    }
                    send_otp(request)
                    return redirect('otp')
                else:
                    messages.error(request, "Password doesn't match")
                    return redirect('sign_up')
        else:
            messages.error(request, 'Method not allowed')
            return redirect('sign_up')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return redirect('home')


def send_otp(request):
    try:
        totp = pyotp.TOTP(pyotp.random_base32(), interval=60)
        otp = totp.now()
        request.session['otp_key'] = totp.secret
        otp_valid = datetime.now() + timedelta(minutes=2)
        request.session['otp_valid'] = str(otp_valid)
        print(f"otp: {otp}")

        email = request.session['mail']
        subject = 'Verify your account'
        msg = f"Your otp is {otp}"
        from_email = 'timezone051199@gmail.com'
        reciever = [email]

        email = EmailMessage(subject, msg, from_email, reciever)
        email.send()
    except Exception as e:
        print(f"{str(e)}")


def resend_otp(request):
    try:
        if request.user.is_authenticated:
            return redirect('home')
        else:
            send_otp(request)
            messages.success(request, 'OTP resent successfully!')
            return redirect('otp')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return redirect('home')


def otp(request):
    try:
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return render(request, 'user/otp.html')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return redirect('home')


def otp_perform(request):
    try:
        if request.method == 'POST':
            otp = request.POST.get('otp')
            user_data = request.session.get('user_data')
            otp_key = request.session.get('otp_key')
            otp_valid = request.session.get('otp_valid')
            if otp_key and otp_valid is not None:
                valid_otp = datetime.fromisoformat(otp_valid)
                print(otp_valid)
                if valid_otp > datetime.now():
                    totp = pyotp.TOTP(otp_key, interval=60)
                    if totp.verify(otp):
                        user = User.objects.create_user(**user_data)
                        request.session['user'] = user.email
                        login(request, user)
                        clear_session(request)
                        return redirect('login_perform')
                    else:
                        messages.error(request, 'OTP invalid')
                        return redirect('otp')
                else:
                    clear_session(request)
                    messages.error(request, 'OTP expired')
                    return redirect('sign_up')
            else:
                clear_session(request)
                messages.error(request, "Didn't get any OTP")
                return redirect('sign_up')
        else:
            clear_session(request)
            return redirect('sign_up')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return redirect('home')


def clear_session(request):
    try:
        keys = ['otp_key', 'otp_valid', 'user_data', 'mail']
        for key in keys:
            if key in request.session:
                del request.session[key]
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
        
@never_cache
def login_perform(request):
    try:
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('admin_dsh')
            else:
                return redirect('home')

        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    if user.is_superuser:
                        login(request, user)
                        return redirect("admin_dsh")
                    else:
                        login(request, user)
                        return redirect("home")
                else:
                    messages.error(request, 'Your account is blocked. Please contact the administrator.')
            else:
                messages.error(request, 'Invalid login credentials or you are not authorized to access this page')

        return render(request, 'user/userlogin.html')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return redirect('home')



@never_cache
def home_perform(request):
    try:
        if not request.user.is_authenticated:
            return render(request, 'user/userlogin.html')
        else:
            return redirect('home')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return redirect('home')


@never_cache
def category_search(request, uid):
    try:
        if request.user.is_authenticated:
            product = Product.objects.filter(category=uid)
            return render(request, 'user/category_page.html', {'product': product})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return redirect('home')


def search(request):
    try:
        query = request.GET.get('query')
        if query:
            product = Product.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)).exclude(
                active=False)
            return render(request, 'user/category_page.html', {'product': product})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return redirect('home')


@never_cache
def view_product(request, pid):
    try:
        vi_product = Product.objects.get(id=pid)
        return render(request, 'user/view_product.html', {'vi_product': vi_product})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return redirect('home')


@login_required(login_url='login_perform')
def log_out(request):
    try:
        request.session.flush()
        logout(request)
        return redirect('home')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return redirect('home')

def product(request):
    try:
        product = Product.objects.all().exclude(active=False)
        category = Category.objects.all().exclude(active=False)
        brand = Brand.objects.all().exclude(active=False)

        return render(request, 'user/product_list.html', {'product': product, 'category': category, 'brand': brand})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return redirect('home')

from datetime import date

def product_view(request, id):
    try:
        
        a = Product.objects.get(id=id)
        
       
        category_offers = CategoryOffer.objects.filter(category=a.category, start_date__lte=date.today(), end_date__gte=date.today())
        
        
        product_offer = ProductOffer.objects.filter(product=a, start_date__lte=date.today(), end_date__gte=date.today())
        
        # Remove the unnecessary line, as the discounted price is already calculated in the model
        # product.get_discounted_price = product.get_discounted_price()

        # Fix the return statement, and correct the dictionary structure
        return render(request, 'user/product_view.html', {'data': a, 'product_offer': product_offer, 'category_offers': category_offers})
    except Product.DoesNotExist:
        pass

    return redirect('home')



def products_view(request):
    try:
        all_products = Product.objects.all()  # Replace with your actual model

        page = request.GET.get('page', 1)
        paginator = Paginator(all_products, 4)  # Show 4 products per page

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver the first page.
            products = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g., 9999), deliver the last page.
            products = paginator.page(paginator.num_pages)

        return render(request, 'your_template.html', {'products': products})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return redirect('home')


def user_profile(request):
    try:
        address = Address.objects.filter(user=request.user)
        return render(request, 'user/userprofile.html', {'address': address})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return redirect('home')


@login_required(login_url='login_perform')
def edit_username_action(request):
    try:
        if request.user.is_authenticated:
            if request.method == 'POST':
                new_username = request.POST.get('new_username')

                # Check if the new username already exists
                if User.objects.filter(username=new_username).exclude(pk=request.user.pk).exists():
                    messages.error(request, 'Username already exists. Please choose a different username.')
                    return redirect('user_profile')

                user = request.user
                user.username = new_username
                user.save()
                messages.success(request, 'Username updated successfully!')
                return redirect('user_profile')
            else:
                # Handle the case if the form is not submitted properly
                messages.error(request, 'Invalid form submission')
                return redirect('user_profile')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return redirect('home')
   
@login_required
def change_password(request):
    try:
        if request.method == 'POST':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')

            if not check_password(old_password, request.user.password):
                return JsonResponse({'message': 'Incorrect old password.'}, status=400)

            if ' ' in new_password:
                return JsonResponse({'message': 'New password cannot contain spaces.'}, status=400)

            request.user.set_password(new_password)
            request.user.save()

            user = authenticate(username=request.user.username, password=new_password)
            if user is not None:
                login(request, user)
                return JsonResponse({'message': 'Password changed successfully.'})
            else:
                return JsonResponse({'message': 'Error authenticating user with new password.'}, status=400)

        return JsonResponse({'message': 'Invalid request.'}, status=400)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return JsonResponse({'message': 'Internal Server Error'}, status=500)




def for_otp(request):
        return render(request, "user/verify_email.html")
   
def forgot_password_action(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'User with the given email does not exist.')
            return render(request, 'user/verify_email.html')

        request.session['id'] = user_obj.id
        request.session['mail'] = email
        send_otp(request)  # Call the send_otp function
        return redirect('forget_otp')

    return render(request, 'user/otptyping.html')



def forget_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        otp_key = request.session.get('otp_key')
        otp_valid = request.session.get('otp_valid')
        if otp_key and otp_valid is not None:
            valid_otp = datetime.fromisoformat(otp_valid)
            if valid_otp > datetime.now():
                totp = pyotp.TOTP(otp_key, interval=60)
                if totp.verify(otp):
                    return redirect('new_password')
                else:
                    messages.error(request, 'Invalid Otp')
                    return redirect('forget_otp')
            else:
                clear_session(request)
                messages.error(request, 'Otp expired')
                return redirect('login_perform')
        else:
            clear_session(request)
            messages.error(request, 'Didnt get any otp')
            return redirect('login_perform')
    return render(request, 'user/otptyping.html')


def resend_otp_forgot(request):
    try:
        if request.user.is_authenticated:
            return redirect('home')
        else:
            send_otp(request)
            messages.success(request, 'OTP resent successfully!')
            return redirect('forget_otp')
    except Exception as e:
        return JsonResponse({'message': 'Internal Server Error'}, status=500)
    
    
from django.contrib.auth import login, authenticate


def new_password(request):
    if request.method == 'POST':
        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')
        if password_1 == password_2:
            id = request.session.get('id')
            user = User.objects.get(id=id)
            hashed_password = make_password(password_1)
            user.password = hashed_password
            user.save()
            print('passwordchanged')
            return redirect('login_perform')
    return render(request, 'user/newpassword.html')


def add_address(request):
    origin_page = request.GET.get('origin_page', 'user_profile')  # Default to 'user_profile' if not provided
    context = {'origin_page': origin_page}
    return render(request, 'user/addaddress.html', context)


def add_address_perform(request):
    try:
        if request.user.is_authenticated:
            if request.method == "POST":
                firstname = request.POST.get('firstname')
                lastname = request.POST.get('lastname')
                address = request.POST.get('address')
                address1 = request.POST.get('address1')
                city = request.POST.get('city')
                zipcode = request.POST.get('zipcode')
                phone = request.POST.get('phone')

                # Assuming user is the authenticated user
                user = request.user

                # Check if an address already exists for the user
                existing_address_id = request.POST.get('existing_address_id')
                existing_address = None

                if existing_address_id:
                    existing_address = get_object_or_404(Address, id=existing_address_id, user=user)

                if existing_address:
                    # If an address already exists, update its fields
                    existing_address.first_name = firstname
                    existing_address.last_name = lastname
                    existing_address.city = city
                    existing_address.zipcode = zipcode
                    existing_address.address = address
                    existing_address.address1 = address1
                    existing_address.phone = phone
                    existing_address.save()
                else:
                    # If no address exists, create and save a new Address object
                    new_address = Address(
                        first_name=firstname,
                        last_name=lastname,
                        address=address,
                        address1=address1,
                        city=city,
                        zipcode=zipcode,
                        phone=phone,
                        user=user
                    )

                    # Validate the address before saving
                    try:
                        new_address.full_clean()
                    except ValidationError as ve:
                        errors = ve.message_dict
                        return JsonResponse({'message': 'Validation Error', 'errors': errors}, status=400)

                    new_address.save()

                origin_page = request.POST.get('origin_page', 'user_profile')
                return redirect(origin_page)

        return JsonResponse({'message': 'Error authenticating user with new password.'}, status=400)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return JsonResponse({'message': 'Internal Server Error'}, status=500)


def delete_address(request, address_id):
    try:
        if request.user.is_authenticated:
            user = request.user

            # Assuming you have an Address model with a ForeignKey to User
            address = get_object_or_404(Address, id=address_id, user=user)

            # Delete the address
            address.delete()

            return redirect('user_profile')
        return JsonResponse({'message': 'Error authenticating user for address deletion.'}, status=400)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return JsonResponse({'message': 'Internal Server Error'}, status=500)


def edit_address_page(request, address_id):
    try:
        # Fetch the address details using the address_id
        address = get_object_or_404(Address, id=address_id)

        # Pass the address details to the template along with the origin_page
        origin_page = request.GET.get('origin_page', 'user_profile')
        return render(request, 'user/editaddress.html', {'address': address, 'origin_page': origin_page})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return JsonResponse({'message': 'Internal Server Error'}, status=500)


def update_address(request, address_id):
    try:
        if request.user.is_authenticated:
            address = get_object_or_404(Address, id=address_id, user=request.user)

            if request.method == "POST":
                # Update the address fields
                address.first_name = request.POST.get('editFirstName')
                address.last_name = request.POST.get('editLastName')
                address.city = request.POST.get('editCity')
                address.zipcode = request.POST.get('editZipcode')
                address.address = request.POST.get('editAddress')
                address.address1 = request.POST.get('editAddress1')
                address.phone = request.POST.get('editPhone')
                address.save()

                origin_page = request.POST.get('origin_page', 'user_profile')
                return redirect(origin_page)

        return JsonResponse({'message': 'Error authenticating user with new password.'}, status=400)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return JsonResponse({'message': 'Internal Server Error'}, status=500)
    
    
def price_filter(request):
    category = Category.objects.all()
    brand = Brand.objects.all()

    # Initialize the queryset without any filtering
    product = Product.objects.all()

    if request.method == "POST":
        min_price = request.POST.get("min_price")
        max_price = request.POST.get("max_price")
        s_category = request.POST.get('category')
        s_brand = request.POST.get('brand')
        sort_order = request.POST.get('sort_order')

        conditions = Q()

        if min_price and max_price:
            try:
                min_price = float(min_price)
                max_price = float(max_price)

                if max_price < min_price:
                    messages.error(request, "Maximum price should be greater than or equal to the minimum price.")
                    return render(request, "user/product_list.html", {'product': product, 'category': category, 'brand': brand})

                conditions &= Q(price__range=(min_price, max_price))

            except ValueError:
                messages.error(request, "Invalid price values")
                return render(request, "user/product_listing.html", {'product': product, 'category': category, 'brand': brand})

        if s_category:
            conditions &= Q(category=s_category)
        
        if s_brand:
            conditions &= Q(brand=s_brand)

        # Apply conditions to the queryset
        product = product.filter(conditions)

        # Order products based on the selected sort_order
        if sort_order == "asc":
            product = product.order_by('price')
        elif sort_order == "desc":
            product = product.order_by('-price')

    context = {
        'product': product,
        'category': category,
        'brand': brand,
    }
    return render(request, "user/product_listing.html", context)

def products(request):
    product = Product.objects.exclude(active=False)
    category = Category.objects.all()
    brand = Brand.objects.all()
        
    context = {
        'product': product,
        'category': category,
        'brand': brand,
    }
    return render(request, 'user/product_listing.html', context)


def view_coupons(request):
    current_date = timezone.now()
    active_coupon = Coupon.objects.filter(active=True, is_expired__gte=current_date)
    return render(request, 'user/usercoupon.html', {'active_coupon': active_coupon})


def search_products(request):
    query = request.GET.get('search_query', '')
    results = Product.objects.filter(title__icontains=query)  # Adjust to use 'title' field
    context = {'product': results}
    return render(request, 'user/product_listing.html', context)

from django.http import HttpResponse

def index(request):
    posts = Post.objects.all()  # Getting all the posts from database
    return render(request, 'user/sample_template.html', { 'posts': posts })

def likePost(request):
    if request.method == 'GET':
           post_id = request.GET['post_id']
           likedpost = Post.objects.get(pk=post_id) #getting the liked posts
           m = Like(post=likedpost) # Creating Like Object
           m.save()  # saving it to store in database
           return HttpResponse("Success!") # Sending an success response
    else:
           return HttpResponse("Request method is not a GET")
