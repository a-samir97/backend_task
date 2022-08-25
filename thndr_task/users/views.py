from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer, UserBalance, StockSerializer
from utils.redis_client import RedisClient
from . import constants

class UserViewSet(GenericViewSet, RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['POST'], serializer_class=UserBalance)
    def deposit(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        user.balance += serializer.validated_data['amount']
        user.save()
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'], serializer_class=UserBalance)
    def withdraw(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        
        if user.balance < serializer.validated_data['amount']:
            return Response(data={"detail": constants.USER_DO_NOT_HAVE_ENOUGH_MONEY_ERR},status=status.HTTP_400_BAD_REQUEST)

        user.balance -= serializer.validated_data['amount']
        user.save()
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'], serializer_class=StockSerializer)
    def buy(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()

        # redis client to get stock info 
        redis_client = RedisClient(host='redis', port=6379)
        stock_data = redis_client.get_stock(name='stocks', key=serializer.validated_data['name'])

        # invalid stock id 
        if not stock_data:
            return Response(data={'detail': constants.INVALID_STOCK_ID_ERR}, status=status.HTTP_404_NOT_FOUND)
        
        # if users wants a number of stocks that does not exist 
        if serializer.validated_data['total'] > stock_data['availability']:
            return Response(
                data={'detail': constants.TOTAL_NUMBER_OF_STOCKS_EXCEEDS_ERR}, 
                status=status.HTTP_400_BAD_REQUEST)

        price_in_user_bounds = serializer.validated_data['lower_bound'] <= stock_data['price'] <= serializer.validated_data['upper_bound']
        if not price_in_user_bounds:
            return Response(data={'detail': constants.PRICE_NOT_IN_USER_BOUNDS_ERR}, status=status.HTTP_400_BAD_REQUEST)

        # need to check if the price between the user bounds and user has enough balance to buy
        user_has_enough_balance = user.balance >= (stock_data['price'] * serializer.validated_data['total'])
        if user_has_enough_balance:
            if user.stocks.get(serializer.validated_data['name']):
                user.stocks[serializer.validated_data['name']] += serializer.validated_data['total']
            else:
                user.stocks[serializer.validated_data['name']] = serializer.validated_data['total']
            user.balance -= (stock_data['price'] * serializer.validated_data['total'])
            user.save()
            return Response(status=status.HTTP_200_OK)

        return Response(
            data={'detail': constants.USER_DO_NOT_HAVE_ENOUGH_MONEY_ERR}, 
            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'], serializer_class=StockSerializer)
    def sell(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()

        # redis client to get stock info 
        redis_client = RedisClient(host='redis', port=6379)
        stock_data = redis_client.get_stock(name='stocks', key=serializer.validated_data['name'])

        # invalid stock id 
        if not stock_data:
            return Response(data={'detail': constants.INVALID_STOCK_ID_ERR}, status=status.HTTP_404_NOT_FOUND)

        # user dont have this stock to sell
        if not user.stocks.get(serializer.validated_data['name']) or \
            user.stocks.get(serializer.validated_data['name'] == 0):
            return Response(data={'detail': constants.USER_DONT_HAVE_STOCK_ERR}, status=status.HTTP_400_BAD_REQUEST)

        # if users wants to sell a number of stocks that does not exist 
        if serializer.validated_data['total'] > user.stocks[serializer.validated_data['name']]:
            return Response(
                data={'detail': constants.TOTAL_NUMBER_OF_STOCKS_EXCEEDS_ERR}, 
                status=status.HTTP_400_BAD_REQUEST)

        price_in_user_bounds = serializer.validated_data['lower_bound'] <= stock_data['price'] <= serializer.validated_data['upper_bound']
        if price_in_user_bounds:
            user.balance += stock_data['price'] * serializer.validated_data['total']
            user.stocks[serializer.validated_data['name']] -= serializer.validated_data['total']
            user.save()
            return Response(status=status.HTTP_200_OK)

        return Response(data={'detail': constants.PRICE_NOT_IN_USER_BOUNDS_ERR}, status=status.HTTP_400_BAD_REQUEST)