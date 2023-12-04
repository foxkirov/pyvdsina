from .templates import ServerTemplate, DataCenter, Account, ServerGroup, ServerPlan, Server, SSHKey
from .baseapi import BaseApi, ApiException
import logging
from typing import Union, List

logger = logging.getLogger(__name__)


class Api(BaseApi):
    def __init__(self, api_token, debug=False):
        super().__init__(api_token, debug)
        self.account = Account(self.get('/account'))
        balance = self.get('/account.balance')
        self.balance = balance['real']
        self.bonus = balance['bonus']
        self.partner = balance['partner']

    def get_limits(self):
        return self.get('/account.limit')

    def register_new_account(self, email):
        return self.post('/register', email=email, code=self._p_code)

    def get_server_groups(self) -> List[ServerGroup]:
        data = []
        groups_list = self.get('/server-group')
        for group in groups_list:
            data.append(ServerGroup(group))

        return data

    def get_dc_list(self) -> List[DataCenter]:
        data = []
        dc_list = self.get('/datacenter')
        for dc in dc_list:
            data.append(DataCenter(dc))

        return data

    def get_dc(self, dc_id) -> DataCenter:
        dc_list = self.get_dc_list()
        for dc in dc_list:
            if dc.id == dc_id:
                return dc

        raise ApiException('DC not found')

    def get_templates(self) -> List[ServerTemplate]:
        data = []
        templates = self.get('/template')
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
        server_plans = self.get('/server-plan/{}'.format(group.id))
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
        ssh_keys = self.get('/ssh-key')
        for ssh_key in ssh_keys:
            data.append(SSHKey(key_id=ssh_key['id'], name=ssh_key['name']))
        return data

    def get_ssh_key(self, key: Union[int, str]) -> SSHKey:
        ssh_keys = self.get('/ssh-key')
        if isinstance(key, int):
            for ssh_key in ssh_keys:
                if ssh_key.key_id == key:
                    return ssh_key

        else:
            for ssh_key in ssh_keys:
                if ssh_key.name == key:
                    return ssh_key

        raise ApiException('Key not found')

    def get_servers(self) -> List[Server]:
        data = []
        servers = self.get('/server')
        for server in servers:
            server_data = self.get('/server/{}'.format(server['id']))
            data.append(Server(server_data))
        return data

    def get_server(self, server_id: int) -> Server:
        data = self.get('/server/{}'.format(server_id))
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

        new_server_data = self.post('/server',
                                    datacenter=datacenter.id,
                                    server_plan=server_plan.id,
                                    template=template.id, ssh_key=ssh_key.key_id if ssh_key else None)
        new_server = self.get('/server/{}'.format(new_server_data['id']))

        return Server(new_server)

    def delete_server(self, server: Union[Server, int]) -> bool:
        """
        :param server: (pyvdsina.Server | int) - server to delete
        :return: boolean - True if server was deleted
        """
        data = self.delete('/server/{}'.format(server.id if isinstance(server, Server) else server))
        return True
