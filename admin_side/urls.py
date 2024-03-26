from django.urls import path
from . import views



urlpatterns = [
    
    path(' error',views.error,name='error'),
    path("admin_dsh",views.admin_dsh,name='admin_dsh'),
    path("show_category",views.show_category,name='show_category'),
    path("add_category",views.add_category,name='add_category'),
    path("add_category_action",views.add_category_action,name='add_category_action'),
    path("edit_category/<int:cid>",views.edit_category,name='edit_category'),
    path("edt_category_action",views.edt_category_action,name='edt_category_action'),
    path("category_action/<int:cid>",views.category_action,name='category_action'),
    path('delete_category/<id>',views.delete_category,name='delete_category'),
    path("show_brand",views.show_brand,name='show_brand'),
    path("add_brand",views.add_brand,name='add_brand'),
    path("admin_delete_product/<id>",views.admin_delete_product,name="admin_delete_product"),
    path("add_brand_action",views.add_brand_action,name='add_brand_action'),
    path("edit_brand/<int:bid>",views.edit_brand,name='edit_brand'),
    path("edt_brand_action",views.edt_brand_action,name='edt_brand_action'),
    path("brand_action/<int:bid>",views.brand_action,name='brand_action'),
    path("show_product",views.show_product,name='show_product'),
    path("delete_brand/<id>",views.delete_brand,name='delete_brand'),
    path("edit_product/<int:uid>",views.edit_product,name='edit_product'),
    path("edit_product_action",views.edit_product_action,name='edit_product_action'),
    path("admin_view_product/<int:uid>",views.admin_view_product,name='admin_view_product'),
    path("add_product",views.add_product,name='add_product'),
    path("show_user",views.show_user,name='show_user'),
    path('customeraction/<int:uid>/', views.customeraction, name='customeraction'),
    path('product_action/<int:uid>/', views.product_action, name='product_action'),
    path('add_product_action', views.add_product_action, name='add_product_action'),
    path('customers/',views.customer_list, name='customer_list'),
    path('order/',views.order,name='order'),
    path('order_view/<int:order_id>/',views.order_view,name='order_view'),
    path('order_update/<int:order_id>/',views.order_update,name='order_update'),
    path('returnedorders',views.returnedorders,name='returnedorders'),
    path('returned_details/<int:id>/',views.returned_details,name='returned_details'),
    path('order_return/<int:order_id>/',views.order_return,name='order_return'),
   
    path('coupon',views.coupon,name='coupon'),
    path('addcoupon',views.addcoupon,name='addcoupon'),
    path('edit_coupon/<int:id>/',views.edit_coupon,name='edit_coupon'),
    path('edit_couponaction',views.edit_couponaction,name='edit_couponaction'),
    path('delete_coupon/<int:id>/', views.delete_coupon, name='delete_coupon'),
    
    path('category_Offer',views.category_Offer,name='category_Offer'),
    path('add_category_Offer',views.add_category_Offer,name='add_category_Offer'),
    path('edit_category_offer/<int:offer_id>/',views.edit_category_offer,name='edit_category_offer'),
    path('delete_category_Offer/<int:offer_id>/',views.delete_category_Offer,name='delete_category_Offer'),
    path('product_Offer',views.product_Offer,name='product_Offer'),
    path('add_product_Offer',views.add_product_Offer,name='add_product_Offer'),
    path('edit_product_offer/<int:offer_id>/',views.edit_product_offer,name='edit_product_offer'),
    path('delete_product_Offer/<int:offer_id>/',views.delete_product_Offer,name='delete_product_Offer'),
    
    path('salesreport',views.salesreport,name='salesreport'),
    path('filter_salesreport',views.filter_salesreport,name='filter_salesreport'),
    path('generate_sales_report_pdf',views.generate_sales_report_pdf,name='generate_sales_report_pdf'),
    
]