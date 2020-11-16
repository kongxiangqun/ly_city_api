from django.urls import path,re_path
from . import views

urlpatterns = [
    path('add_cart/', views.AddCartView.as_view(
        {'post':'add','get':'cart_list',
         'patch':'change_select',
         'put':'cancel_select',
         'delete':'delete_course'
         })),
    path('expires/', views.AddCartView.as_view({'put':'change_expire','get':'show_pay_info'}))
]
