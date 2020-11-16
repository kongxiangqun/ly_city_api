from django.urls import path,re_path
from . import views

urlpatterns = [
    path('alipay/',views.AlipayView.as_view(),),
    path('result/',views.AlipayResultView.as_view(),)

]