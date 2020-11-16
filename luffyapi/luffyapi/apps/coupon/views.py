from django.shortcuts import render
from rest_framework.generics import ListAPIView
# Create your views here.
from . import models
from rest_framework.permissions import IsAuthenticated

from .serializers import UserCouponModelSerializer


class CouponView(ListAPIView):

    serializer_class = UserCouponModelSerializer
    permission_classes = [IsAuthenticated, ]
    def get_queryset(self):

        return models.UserCoupon.objects.filter(is_show=True,is_deleted=False,is_use=False, user_id=self.request.user.id)


