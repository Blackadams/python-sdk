from .client import Client


class Simulator(Client):

    def __init__(self, org_id, api_key, app_id, options):
        super().__init__(org_id, api_key, app_id, options)
        self.is_simulator = True

