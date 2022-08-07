
class SeverTemplate(object):

    def __init__(self, data=dict):
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
    def __init__(self, data=dict):
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
    def __init__(self, data=dict):
        self.id = data['id']
        self.name = data['name']
        self.country = data['country']
        self.active = data['active']
        self.data = data

    def __str__(self):
        return self.country


class Account(object):
    def __init__(self, data):
        self.id = data['account']['id']
        self.name = data['account']['name']
        self.created_date = data['created']
        self.forecast = data['forecast']
        self.can_add_user = data['can']['add_user']
        self.can_add_service = data['can']['add_service']
        self.can_convert_to_cash = data['can']['convert_to_cash']

    def __str__(self):
        return self.name

