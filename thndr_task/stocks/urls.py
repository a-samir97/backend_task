from rest_framework.routers import DefaultRouter
from .views import StockViewSet

router = DefaultRouter()

router.register('stocks', StockViewSet, 'stock-viewsets')

urlpatterns = router.urls
