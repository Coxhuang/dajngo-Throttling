from django.shortcuts import render
from app import models
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import permissions
from rest_framework.throttling import UserRateThrottle
from rest_framework.throttling import AnonRateThrottle
from app.throttling import getCaptchasStatus
from rest_framework.response import Response
from django.shortcuts import Http404

class viewSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = "__all__"

class view(mixins.ListModelMixin,GenericViewSet):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (permissions.AllowAny,)
    # throttle_classes = (UserRateThrottle,)
    # throttle_no_scope = "myThrottlingChackCaptchas" # 自定义节流
    throttle_scope = "uploads"
    serializer_class = viewSerializer
    queryset = models.UserProfile.objects.all()


    def list(self, request, *args, **kwargs):
        if getCaptchasStatus(): # 当超过次数后, 会进入这个条件
            print("限制")
            raise Http404("限制")
        else:
            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)




