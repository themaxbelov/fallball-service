from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers

from fb.views import ClientViewSet, ResellerViewSet, ClientUserViewSet

router = routers.DefaultRouter()
router.register(r'resellers', ResellerViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'users', ClientUserViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
]
