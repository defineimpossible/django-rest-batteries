from rest_framework import routers

from .views import OrderViewSet

router = routers.DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = router.urls
