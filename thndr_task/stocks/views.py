from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework import status
from utils.redis_client import RedisClient

class StockViewSet(GenericViewSet, RetrieveModelMixin):

    def retrieve(self, request, *args, **kwargs):
        redis_instance = RedisClient(host='redis', port=6379)
        stock_data = redis_instance.get_stock(name='stocks', key=str(self.kwargs['pk']))
        if stock_data:
            return Response(data=stock_data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)