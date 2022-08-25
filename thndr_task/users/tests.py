import json
from django.test import TestCase
from unittest import mock
from .models import User
from rest_framework import status
from . import constants

class TestUserAPIs(TestCase):

    def setUp(self) -> None:
        # set up user object
        self.user = User.objects.create(full_name='Test Test', balance=1000.0, stocks={'CIB': 2})

        # set up urls 
        self.user_details_url = '/api/users/{id}/'
        self.deposit_url = '/api/users/{id}/deposit/'
        self.withdraw_url = '/api/users/{id}/withdraw/'
        self.sell_url = '/api/users/{id}/sell/'
        self.buy_url = '/api/users/{id}/buy/'

    def tearDown(self) -> None:
        User.objects.all().delete()

    def test_get_user_api_success_case(self):
        resp = self.client.get(self.user_details_url.format(id=self.user.id))
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

        self.assertEquals(resp.data['balance'], self.user.balance)
        self.assertEquals(resp.data['stocks'], self.user.stocks)
        self.assertEquals(resp.data['full_name'], self.user.full_name)

    def test_get_user_api_no_user_failure_case(self):
        resp = self.client.get(self.user_details_url.format(id=1000000))
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_deposit_api_success_case(self):
        data = {
            'amount': 100
        }
        resp = self.client.post(self.deposit_url.format(id=self.user.id), data=data)
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    def test_user_deposit_api_no_data_failure_case(self):

        resp = self.client.post(self.deposit_url.format(id=self.user.id))
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(resp.data)
        self.assertIn('amount', resp.data)

    def test_user_deposit_api_user_not_exist_failure_case(self):
        data = {
            'amount': 100
        }
        resp = self.client.post(self.deposit_url.format(id=10000), data=data)
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_withdraw_api_sucess_case(self):
        data = {
            'amount': 100
        }
        resp = self.client.post(self.withdraw_url.format(id=self.user.id), data=data)

        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    def test_user_withdraw_api_user_not_exist_failure_case(self):
        data = {
            'amount': 100
        }
        resp = self.client.post(self.withdraw_url.format(id=100000), data=data)

        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_withdraw_api_no_enough_balance_failure_case(self):
        data = {
            'amount': 10000.0
        }
        resp = self.client.post(self.withdraw_url.format(id=self.user.id), data=data)

        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(resp.data['detail'], constants.USER_DO_NOT_HAVE_ENOUGH_MONEY_ERR)

    def test_user_withdraw_api_no_data_failure_case(self):
        resp = self.client.post(self.withdraw_url.format(id=self.user.id))

        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(resp.data)
        self.assertIn('amount', resp.data) 

    @mock.patch('utils.redis_client.RedisClient.get_stock')
    @mock.patch('redis.Redis.ping')
    def test_user_sell_api_success_case(self, mock_redis_ping, mock_redis):
        mock_redis_ping.return_value = True
        mock_redis.return_value = {
            "name": "CIB",
            "stock_id": "0e7dc13b-7f53-497f-9d2d-895e71bf050c",
            "price": 20,
            "availability": 82,
            "timestamp": "2022-08-25 20:27:09.328187"   
        }
        data = {
            'name': 'CIB',
            'total': 1,
            'lower_bound': 10,
            'upper_bound': 1000
        }
        resp = self.client.post(self.sell_url.format(id=self.user.id), data=data)
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    @mock.patch('utils.redis_client.RedisClient.get_stock')
    @mock.patch('redis.Redis.ping')
    def test_user_sell_api_price_not_in_user_bounds_failure_case(self, mock_redis_ping, mock_redis):
        mock_redis_ping.return_value = True
        mock_redis.return_value = {
            "name": "CIB",
            "stock_id": "0e7dc13b-7f53-497f-9d2d-895e71bf050c",
            "price": 1,
            "availability": 82,
            "timestamp": "2022-08-25 20:27:09.328187"   
        }
        data = {
            'name': 'CIB',
            'total': 1,
            'lower_bound': 10,
            'upper_bound': 1000
        }
        resp = self.client.post(self.sell_url.format(id=self.user.id), data=data)
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(resp.data['detail'], constants.PRICE_NOT_IN_USER_BOUNDS_ERR)

    @mock.patch('utils.redis_client.RedisClient.get_stock')
    @mock.patch('redis.Redis.ping')
    def test_user_sell_api_total_stocks_exceeds_failure_case(self, mock_redis_ping, mock_redis_get):
        mock_redis_ping.return_value = True
        mock_redis_get.return_value = {
            "name": "CIB",
            "stock_id": "0e7dc13b-7f53-497f-9d2d-895e71bf050c",
            "price": 1,
            "availability": 82,
            "timestamp": "2022-08-25 20:27:09.328187"   
        }
        data = {
            'name': 'CIB',
            'total': 10,
            'lower_bound': 10,
            'upper_bound': 1000
        }
        resp = self.client.post(self.sell_url.format(id=self.user.id), data=data)
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(resp.data['detail'], constants.TOTAL_NUMBER_OF_STOCKS_EXCEEDS_ERR)

    @mock.patch('utils.redis_client.RedisClient.get_stock')
    @mock.patch('redis.Redis.ping')
    def test_user_buy_api_sucess_case(self, mock_redis_ping, mock_redis_get):
        mock_redis_ping.return_value = True
        mock_redis_get.return_value = {
            "name": "CIB",
            "stock_id": "0e7dc13b-7f53-497f-9d2d-895e71bf050c",
            "price": 20,
            "availability": 82,
            "timestamp": "2022-08-25 20:27:09.328187"   
        }
        data = {
            'name': 'CIB',
            'total': 1,
            'lower_bound': 10,
            'upper_bound': 1000
        }
        resp = self.client.post(self.buy_url.format(id=self.user.id), data=data)
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    @mock.patch('utils.redis_client.RedisClient.get_stock')
    @mock.patch('redis.Redis.ping')
    def test_user_buy_api_price_not_in_user_bounds_failure_case(self, mock_redis_ping, mock_redis_get):
        mock_redis_ping.return_value = True
        mock_redis_get.return_value = {
            "name": "CIB",
            "stock_id": "0e7dc13b-7f53-497f-9d2d-895e71bf050c",
            "price": 1,
            "availability": 82,
            "timestamp": "2022-08-25 20:27:09.328187"   
        }
        data = {
            'name': 'CIB',
            'total': 1,
            'lower_bound': 10,
            'upper_bound': 1000
        }
        resp = self.client.post(self.buy_url.format(id=self.user.id), data=data)
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(resp.data['detail'], constants.PRICE_NOT_IN_USER_BOUNDS_ERR)
