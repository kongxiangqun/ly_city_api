from django.urls import path,re_path
from . import views

urlpatterns = [
    path(r'categorys/', views.CategoryView.as_view(),),
    path(r'courses/', views.CourseView.as_view(),),
    re_path(r'detail/(?P<pk>\d+)/', views.CourseDetailView.as_view(),),
    re_path(r'chapter/', views.ChapterView.as_view(),),

    re_path(r'polyv/token/', views.PolyvView.as_view(),),
]