import requests
from .templates import Resp, ServerTemplate, DataCenter, Account, ServerGroup, ServerPlan, Server
import json
import logging

logger = logging.getLogger(__name__)


class ApiException(Exception):
    def __init__(self, *args, **kwargs):
        pass


def check_errors(_func):
    def wrapper(self, *args, **kwargs):
        response = _func(self, *args, **kwargs)

        if response.status == 'error':
            raise ApiException(f'{response.status_code} {response.status_msg}')

        else:
            logging.debug(f'{response.status_msg}: {response.data}')

            return response.data

    return wrapper


class Api(object):
    _api_url = 'https://userapi.vdsina.ru/v1'
    _p_code = 'kt2rbwyjh8'
    balance = None
    bonus = None
    partner = None

    def __init__(self, api_token, debug=False):
        self.api_token = api_token
        self.debug = debug
        self._headers = {'Authorization': self.api_token, 'Content-Type': 'application/json'}
        self.account = self._get_account()
        self.update_balance()

    def update_balance(self):
        balance = self._get_balance()
        self.balance = balance['real']
        self.bonus = balance['bonus']
        self.partner = balance['partner']

    @check_errors
    def _get_info(self):
        endpoint = '/account'
        r = requests.get(url=self._api_url + endpoint, headers=self._headers)
        return Resp(**r.json())

    def _get_account(self):
        account = self._get_info()
        return Account(account)

    @check_errors
    def _get_balance(self):
        endpoint = '/account.balance'
        r = requests.get(url=self._api_url + endpoint, headers=self._headers)
        return Resp(**r.json())

    @check_errors
    def get_limits(self):
        endpoint = '/account.limit'
        r = requests.get(url=self._api_url + endpoint, headers=self._headers)
        return Resp(**r.json())

    @check_errors
    def register_new_account(self, email):
        endpoint = '/register'
        params = {"email": email,
                  "code": self._p_code}

        r = requests.post(url=self._api_url + endpoint, headers=self._headers, json=params)
        return Resp(**r.json())

    @check_errors
    def _get_server_groups(self):
        endpoint = '/server-group'
        r = requests.get(url=self._api_url + endpoint, headers=self._headers)
        return Resp(**r.json())

    def get_server_groups(self):
        data = []
        groups_list = self._get_server_groups()
        for group in groups_list:
            data.append(ServerGroup(group))

        return data

    @check_errors
    def _get_dc_list(self):
        endpoint = '/datacenter'
        r = requests.get(url=self._api_url + endpoint, headers=self._headers)
        return Resp(**r.json())

    def get_dc_list(self):
        data = []
        dc_list = self._get_dc_list()
        for dc in dc_list:
            data.append(DataCenter(dc))

        return data

    def get_dc(self, dc_id):
        dc_list = self.get_dc_list()
        for dc in dc_list:
            if dc.id == dc_id:
                return dc

        return None

    @check_errors
    def _get_templates(self):
        endpoint = '/template'
        r = requests.get(url=self._api_url + endpoint, headers=self._headers)
        return Resp(**r.json())

    def get_templates(self):
        data = []
        templates = self._get_templates()
        for template in templates:
            data.append(ServerTemplate(template))

        return data

    def get_template(self, template_id: int):
        templates_list = self.get_templates()
        for template in templates_list:
            if template.id == template_id:
                return template

        return None

    @check_errors
    def _get_server_plans(self, group: ServerGroup):
        endpoint = f'/server-plan/{group.id}'
        r = requests.get(url=self._api_url + endpoint, headers=self._headers)
        return Resp(**r.json())

    def get_server_plans(self, group: ServerGroup):
        data = []
        server_plans = self._get_server_plans(group)
        for plan in server_plans:
            data.append(ServerPlan(plan))

        return data

    def get_server_plan(self, plan_id: int):
        server_groups = self.get_server_groups()
        for group in server_groups:
            server_plans = self.get_server_plans(group=group)
            for plan in server_plans:
                if plan.id == plan_id:
                    return plan

        return None

    def get_ssh_keys(self):
        endpoint = '/ssh-key'
        r = requests.get(url=self._api_url + endpoint, headers=self._headers)
        return Resp(**r.json())

    @check_errors
    def _get_servers(self):
        endpoint = '/server'
        r = requests.get(url=self._api_url + endpoint, headers=self._headers)
        return Resp(**r.json())

    @check_errors
    def _get_server(self, server_id: int):
        endpoint = f'/server/{server_id}'
        r = requests.get(url=self._api_url + endpoint, headers=self._headers)
        return Resp(**r.json())

    def get_servers(self):
        data = []
        servers = self._get_servers()
        for server in servers:
            server_data = self._get_server(server['id'])
            data.append(Server(server_data))
        return data

    @check_errors
    def _post_server(self, datacenter_id: int, server_plan_id: int, template_id: int):
        endpoint = f'/server'
        params = {"datacenter": datacenter_id, "server-plan": server_plan_id, "template": template_id}
        r = requests.post(url=self._api_url + endpoint, headers=self._headers, data=json.dumps(params))
        return Resp(**r.json())

    def simple_create_server(self, dc_id: int, server_plan_id: int, template_id: int):
        new_server_data = self._post_server(datacenter_id=dc_id,
                                            server_plan_id=server_plan_id,
                                            template_id=template_id)
        new_server = self._get_server(server_id=new_server_data["id"])

        return Server(new_server)

    def create_server(self, datacenter: DataCenter, server_plan: ServerPlan, template: ServerTemplate):
        new_server_data = self._post_server(datacenter_id=datacenter.id,
                                            server_plan_id=server_plan.id,
                                            template_id=template.id)
        new_server = self._get_server(server_id=new_server_data["id"])

        return Server(new_server)

    @check_errors
    def _delete_server(self, server_id: int):
        endpoint = f'/server/{server_id}'
        r = requests.delete(url=self._api_url + endpoint, headers=self._headers)
        return Resp(**r.json())

    def simple_delete_server(self, server_id: int):
        data = self._delete_server(server_id=server_id)
        return True

    def delete_server(self, server: Server):
        data = self._delete_server(server.id)
        return True
