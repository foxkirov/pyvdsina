from .templates import ServerTemplate, DataCenter, Account, ServerGroup, ServerPlan, Server, SSHKey, Resp
import requests
import logging
from typing import Union, List


logger = logging.getLogger(__name__)


class ApiException(Exception):
    pass


class Api(object):
    _p_code = 'kt2rbwyjh8'
    _api_url = 'https://userapi.vdsina.ru/v1'
    def __init__(self, api_token: str, debug: bool = False):
        self.api_token = api_token
        self.debug = debug
        self._headers = {'Authorization': self.api_token, 'Content-Type': 'application/json'}
        self.account = Account(self._get('/account'))
        self.update_balance()

    @staticmethod
    def replace_keys(data: dict) -> dict:
        return {k.replace('_', '-'): v for k, v in data.items()}

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
    def _get(self, endpoint, **params):
        r = requests.get(url=self._api_url + endpoint, headers=self._headers, params=self.replace_keys(params))
        return Resp(**r.json())

    @check_errors
    def _post(self, endpoint, **params):
        r = requests.post(url=self._api_url + endpoint, headers=self._headers, json=self.replace_keys(params))
        return Resp(**r.json())

    @check_errors
    def _put(self, endpoint, **params):
        r = requests.put(url=self._api_url + endpoint, headers=self._headers, json=self.replace_keys(params))
        return Resp(**r.json())

    @check_errors
    def _delete(self, endpoint, **params):
        r = requests.delete(url=self._api_url + endpoint, headers=self._headers, params=self.replace_keys(params))
        return Resp(**r.json())

    def update_balance(self):
        balance = self._get('/account.balance')
        self.balance = balance['real']
        self.bonus = balance['bonus']
        self.partner = balance['partner']

    def get_limits(self):
        return self._get('/account.limit')

    def register_new_account(self, email: str):
        return self._post('/register', email=email, code=self._p_code)

    def get_server_groups(self) -> List[ServerGroup]:
        data = []
        groups_list = self._get('/server-group')
        for group in groups_list:
            data.append(ServerGroup(group))

        return data

    def get_dc_list(self) -> List[DataCenter]:
        data = []
        dc_list = self._get('/datacenter')
        for dc in dc_list:
            data.append(DataCenter(dc))

        return data

    def get_dc(self, dc_id: int) -> DataCenter:
        dc_list = self.get_dc_list()
        for dc in dc_list:
            if dc.id == dc_id:
                return dc

        raise ApiException('DC not found')

    def get_templates(self) -> List[ServerTemplate]:
        data = []
        templates = self._get('/template')
        for template in templates:
            data.append(ServerTemplate(template))

        return data

    def get_template(self, template_id: int) -> ServerTemplate:
        templates_list = self.get_templates()
        for template in templates_list:
            if template.id == template_id:
                return template

        raise ApiException('Template not found')

    def get_server_plans(self, group: ServerGroup) -> List[ServerPlan]:
        data = []
        server_plans = self._get('/server-plan/{}'.format(group.id))
        for plan in server_plans:
            data.append(ServerPlan(plan))

        return data

    def get_server_plan(self, plan_id: int) -> ServerPlan:
        server_groups = self.get_server_groups()
        for group in server_groups:
            server_plans = self.get_server_plans(group=group)
            for plan in server_plans:
                if plan.id == plan_id:
                    return plan

        raise ApiException('Server plan not found')

    def get_ssh_keys(self) -> List[SSHKey]:
        data = []
        ssh_keys = self._get('/ssh-key')
        for ssh_key in ssh_keys:
            data.append(SSHKey(key_id=ssh_key['id'], name=ssh_key['name']))
        return data

    def get_ssh_key(self, key: Union[int, str]) -> SSHKey:
        ssh_keys = self.get_ssh_keys()
        if isinstance(key, int):
            for ssh_key in ssh_keys:
                if ssh_key.key_id == key:
                    return ssh_key

        else:
            for ssh_key in ssh_keys:
                if ssh_key.name == key:
                    return ssh_key

        raise ApiException('Key not found')

    def create_ssh_key(self, key: SSHKey) -> SSHKey:
        ssh_key = self._post('/ssh-key', name=key.name, data=key.data)
        return SSHKey(ssh_key)

    def change_ssh_key(self, key: SSHKey) -> SSHKey:
        ssh_key = self._put('/ssh-key/{}'.format(key.key_id),
                           name=key.name, data=key.data)
        return SSHKey(ssh_key)

    def delete_ssh_key(self, key: Union[int, SSHKey]) -> bool:
        ssh_key = self._delete('/ssh-key/{}'.format(key.key_id if isinstance(key, SSHKey) else key))
        return True

    def get_servers(self) -> List[Server]:
        data = []
        servers = self._get('/server')
        for server in servers:
            server_data = self._get('/server/{}'.format(server['id']))
            data.append(Server(server_data))
        return data

    def get_server(self, server_id: int) -> Server:
        data = self._get('/server/{}'.format(server_id))
        return Server(data)

    def create_server(self,
                      datacenter: Union[DataCenter, str],
                      server_plan: Union[ServerPlan, int],
                      template: Union[ServerTemplate, int],
                      ssh_key: Union[SSHKey, int] = None) -> Server:
        """
        :param datacenter: (pyvdsina.Datacenter | str) - datacenter or country code to create
        :param server_plan: (pyvdsina.ServerPlan | int) - server plan or server plan id to create
        :param template: (pyvdsina.ServerTemplate | int) - server template or server template id to create
        :param ssh_key: (pyvdsina.SSHKey | int) - optional ssh key or ssh key id to create
        :return: pyvdsina.Server - created server
        """
        if isinstance(datacenter, str):
            dc_list = self.get_dc_list()
            for dc in dc_list:
                if dc.country == datacenter:
                    datacenter = dc
                    break

            if isinstance(datacenter, str):
                raise ApiException('No datacenter named {}'.format(datacenter))

        if isinstance(server_plan, int):
            server_groups = self.get_server_groups()
            for group in server_groups:
                server_plan_list = self.get_server_plans(group=group)
                for plan in server_plan_list:
                    if plan.id == server_plan:
                        server_plan = plan
                        break

            if isinstance(server_plan, int):
                raise ApiException('No server plan with id {}'.format(server_plan))

        if isinstance(template, int):
            template_list = self.get_templates()
            for _template in template_list:
                if _template.id == template:
                    template = _template
                    break

            if isinstance(template, int):
                raise ApiException('No template with id {}'.format(template))

        if isinstance(ssh_key, int):
            ssh_key_list = self.get_ssh_keys()
            for key in ssh_key_list:
                if key.key_id == ssh_key:
                    ssh_key = key
                    break

            if isinstance(ssh_key, int):
                raise ApiException('No ssh key with id {}'.format(ssh_key))

        new_server_data = self._post('/server',
                                    datacenter=datacenter.id,
                                    server_plan=server_plan.id,
                                    template=template.id, ssh_key=ssh_key.key_id if ssh_key else None)
        new_server = self._get('/server/{}'.format(new_server_data['id']))

        return Server(new_server)

    def delete_server(self, server: Union[Server, int]) -> bool:
        """
        :param server: (pyvdsina.Server | int) - server to delete
        :return: boolean - True if server was deleted
        """
        self._delete('/server/{}'.format(server.id if isinstance(server, Server) else server))
        return True
