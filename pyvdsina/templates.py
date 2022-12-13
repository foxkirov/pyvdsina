class Resp:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class ServerTemplate(object):

    def __init__(self, data: dict):
        self.id = data['id']
        self.name = data['name']
        self.image = data['image']
        self.active = data['active']
        self.has_instruction = data['has_instruction']
        self.limits = data['limits']
        self.ssh_key = data['ssh-key']
        self.server_plan = data['server-plan']
        self.data = data

    def __str__(self):
        return self.name


class ServerGroup(object):
    def __init__(self, data: dict):
        self.id = data['id']
        self.name = data['name']
        self.type = data['type']
        self.image = data['image']
        self.active = data['active']
        self.description = data['description']
        self.data = data

    def __str__(self):
        return self.name


class DataCenter(object):
    def __init__(self, data: dict):
        self.id = data['id']
        self.name = data['name']
        self.country = data['country']
        self.active = data['active']
        self.data = data

    def __str__(self):
        return self.country


class Account(object):
    def __init__(self, data: dict):
        self.id = data['account']['id']
        self.name = data['account']['name']
        self.created_date = data['created']
        self.forecast = data['forecast']
        self.can_add_user = data['can']['add_user']
        self.can_add_service = data['can']['add_service']
        self.can_convert_to_cash = data['can']['convert_to_cash']

    def __str__(self):
        return self.name


class ServerPlan(object):
    class ServerPlanBackup(object):
        def __init__(self, data: dict):
            self.cost = data['cost']
            self.unit = data['for']
            self.full_cost = data['full_cost']
            self.period = data['period']
            self.period_name = data['period_name']

    def __init__(self, data: dict):
        self.active = data['active']
        self.backup = self.ServerPlanBackup(data['backup'])
        self.can_bonus = data['can_bonus']
        self.cost = data['cost']
        self.server_data = data['data']
        self.description = data['description']
        self.enable = data['enable']
        self.full_cost = data['full_cost']
        self.has_params = data['has_params']
        self.id = data['id']
        self.min_money = data['min_money']
        self.name = data['name']
        self.params = data['params'] if 'params' in data.keys() else None
        self.period = data['period']
        self.period_name = data['period_name']
        self.selected = data['selected']
        self.server_group = data['server-group']

    def __str__(self):
        return self.name


class SSHKey(object):
    def __init__(self, name=None, data=None, key_id=None):
        self.key_id = key_id
        self.name = name
        self.data = data


class Server(object):
    def __init__(self, data: dict):
        self.id = data['id']
        self.name = data['name']
        self.status = data['status']
        self.created = data['created']
        self.updated = data['updated']
        self.end = data['end']
        self.autoprolong = data['autoprolong']
        self.ip = data['ip']
        self.ip_local = data['ip_local']
        self.host = data['host']
        self.data = data['data']
        self.server_plan = data['server-plan']
        self.server_group = data['server-group']
        self.template = data['template']
        self.datacenter = data['datacenter']
        self.ssh_key = data['ssh-key']
        self.can = data['can']
        self.bandwidth = data['bandwidth']

    def __str__(self):
        return str(self.id)

