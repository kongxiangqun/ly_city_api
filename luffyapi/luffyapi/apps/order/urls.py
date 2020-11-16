from django.urls import path,re_path
from . import views

urlpatterns = [
    path('add_money/',views.OrderView.as_view(),)

]