import requests
import logging
from .templates import Resp

logger = logging.getLogger(__name__)


class ApiException(Exception):
    pass


class BaseApi(object):
    _api_url = 'https://userapi.vdsina.ru/v1'
    _p_code = 'kt2rbwyjh8'

    def __init__(self, api_token, debug=False):
        self.api_token = api_token
        self.debug = debug
        self._headers = {'Authorization': self.api_token, 'Content-Type': 'application/json'}

    @staticmethod
    def check_errors(func):
        def wrapper(self, *args, **kwargs):
            response = func(self, *args, **kwargs)

            if response.status == 'error':
                logger.error('ApiException {} {}'.format(response.status_code, response.status_msg))
                raise ApiException('{} {}'.format(response.status_code, response.status_msg))

            else:
                logger.debug('{}: {}'.format(response.status_msg, response.data))

                return response.data

        return wrapper

    @check_errors
    def get(self, endpoint, **params):
        correct_params = {k.replace('_', '-'): v for k, v in params.items()}
        r = requests.get(url=self._api_url + endpoint, headers=self._headers, params=correct_params)
        return Resp(**r.json())

    @check_errors
    def post(self, endpoint, **params):
        correct_params = {k.replace('_', '-'): v for k, v in params.items()}
        r = requests.post(url=self._api_url + endpoint, headers=self._headers, json=correct_params)
        return Resp(**r.json())

    @check_errors
    def put(self, endpoint, **params):
        correct_params = {k.replace('_', '-'): v for k, v in params.items()}
        r = requests.put(url=self._api_url + endpoint, headers=self._headers, json=correct_params)
        return Resp(**r.json())

    @check_errors
    def delete(self, endpoint, **params):
        correct_params = {k.replace('_', '-'): v for k, v in params.items()}
        r = requests.delete(url=self._api_url + endpoint, headers=self._headers, params=correct_params)
        return Resp(**r.json())
