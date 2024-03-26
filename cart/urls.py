

from django.urls import path
from cart import views


urlpatterns = [
    path('add_to_cart/<int:uid>/', views.add_to_cart, name='add_to_cart'),
    path("cart/", views.cart, name='cart'),
    path("wishlist", views.wishlist, name='wishlist'),
    path("checkout/", views.checkout, name='checkout'),
    path('remove_cart_item/<int:id>/',views.remove_cart_item, name='remove_cart_item'),
    path('update_cart/<int:id>/<str:action>/', views.update_cart, name='update_cart'),
    path('update_quantity/<int:cart_item_id>/<str:action>/', views.update_quantity, name='update_quantity'),
    path('wishlist', views.wishlist , name='wishlist'),
    path('add_to_wishlist/<int:id>/', views.add_to_wishlist , name='add_to_wishlist'),
    path('wish_remove/<int:id>/', views.wish_remove , name='wish_remove'),
    path('order_success', views.order_success , name='order_success'),
    path('place_order', views.place_order , name='place_order'),
    path('order_listing', views.order_listing , name='order_listing'),
    path('order_detailview/<int:id>/', views.order_detailview , name='order_detailview'),
    path('cancel_order/<int:order_id>/', views.cancel_order , name='cancel_order'),
    path('return_order/<int:order_id>/', views.return_order , name='return_order'),
    path('wallet', views.wallet , name='wallet'),
    path('paymentsuccessful/<int:address>/', views.paymentsuccessful, name='paymentsuccessful'),
    path('paymentfailed', views.paymentfailed, name='paymentfailed'),
    path('base2', views.base2, name='base2'),
    path('order/<int:id>/download_invoice/',views.download_invoice, name='download_invoice'),
]

