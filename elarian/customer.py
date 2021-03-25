

class Customer:
    """..."""
    customer_id: str = None
    customer_number: dict = None

    identity_state: dict = None
    messaging_state: dict = None
    payment_state: dict = None
    activity_state: dict = None

    _client = None

    def __init__(self, client, id=None, number=None, provider=None):
        self._client = client
        if id is not None:
            self.customer_id = id
        if number is not None and provider is not None:
            self.customer_number = {
                'number': number,
                'provider': provider
            }

    async def get_state(self):
        """ Get customer state """
        pass

    async def adopt_state(self, other_customer):
        """ Adopt another customer's state """
        pass

    async def send_message(self, messaging_channel: dict, message: dict):
        """ Send a message """
        pass

    async def reply_to_message(self, message_id: str, message: dict):
        """ Send customer a message """
        pass

    async def update_activity(self, activity_channel: dict, activity: dict):
        """ Update customer's activity """
        pass

    async def update_messaging_consent(self, messaging_channel: dict, action: str):
        """ Update customer's engagement consent on this channel """
        pass

    async def lease_app_data(self):
        """ Lease customer's app data """
        pass

    async def update_app_data(self, data: dict):
        """ Update customer's app data """
        pass

    async def delete_app_data(self):
        """ Remove customer's app data """
        pass

    async def update_metadata(self, data: dict):
        """ Update customer's metadata """
        pass

    async def delete_metadata(self, keys: list):
        """ Remove customer's metadata """
        pass

    async def update_secondary_ids(self, secondary_ids: list):
        """ Update customer's secondary ids """
        pass

    async def delete_secondary_ids(self, secondary_ids: list):
        """ Remove customer's secondary ids """
        pass

    async def update_tags(self, tags: list):
        """ Update a customer's tags """
        pass

    async def delete_tags(self, keys: list):
        """ Remove a customer's tags """
        pass

    async def add_reminder(self, reminder: dict):
        """ Add a reminder """
        pass

    async def cancel_reminder(self, key: str):
        """ Cancel a reminder """
        pass
