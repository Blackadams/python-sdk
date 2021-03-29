from .utils.generated.app_socket_pb2 import AppToServerCommand, AppToServerCommandReply
from .utils.generated.common_model_pb2 import CustomerIndex, IndexMapping
from .utils.helpers import has_key, fill_in_outgoing_message
from .models import *


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
        if number is not None:
            provider = provider if provider is not None else CustomerNumberProvider.CELLULAR
            self.customer_number = {
                'number': number,
                'provider': provider
            }

        if self.customer_id is None and self.customer_number is None:
            raise RuntimeError("Either id or number is required")

    async def get_state(self):
        """ Get customer state """
        req = AppToServerCommand()

        if self.customer_id is not None:
            req.get_customer_state.customer_id = self.customer_id
        elif self.customer_number is not None and has_key('number', self.customer_number):
            req.get_customer_state.customer_number.number = self.customer_number.get('number')
            req.get_customer_state.customer_number.provider = self.customer_number.get('provider', CustomerNumberProvider.CELLULAR).value
        else:
            raise RuntimeError('Invalid customer id and/or customer number')

        data = await self._send_command(req)
        res = self._parse_reply(data).get_customer_state

        if not res.status:
            raise RuntimeError(res.description)
        res = res.data
        self.customer_id = res.customer_id
        return {  # FIXME: Format object accordingly
            "customer_id": res.customer_id,
            "identity_state": res.identity_state,
            "messaging_state": res.messaging_state,
            "payment_state": res.payment_state,
            "activity_state": res.activity_state
        }

    async def adopt_state(self, other_customer):
        """ Adopt another customer's state """
        req = AppToServerCommand()

        if self.customer_id is None:
            await self.get_state()

        req.adopt_customer_state.customer_id = self.customer_id

        if other_customer.customer_id is not None:
            req.adopt_customer_state.customer_id = other_customer.customer_id
        elif other_customer.customer_number is not None and has_key('number', other_customer.customer_number):
            req.adopt_customer_state.customer_number.number = other_customer.customer_number.get('number')
            req.adopt_customer_state.customer_number.provider = other_customer.customer_number.get('provider',
                                                                                       CustomerNumberProvider.CELLULAR).value
        else:
            raise RuntimeError('Invalid customer id and/or customer number')

        data = await self._send_command(req)
        res = self._parse_reply(data).update_customer_state

        if not res.status:
            raise RuntimeError(res.description)

        return {
            "status": res.status,
            "description": res.description,
            "customer_id": res.customer_id.value
        }

    async def send_message(self, messaging_channel: dict, message: dict):
        """ Send a message to this customer"""
        req = AppToServerCommand()
        req.send_message.channel_number.number = messaging_channel.get('number')
        req.send_message.channel_number.channel = messaging_channel.get('channel', MessagingChannel.UNKNOWN).value
        req.send_message.customer_number.number = self.customer_number.get('number')
        req.send_message.customer_number.provider = self.customer_number.get('provider', CustomerNumberProvider.CELLULAR).value
        req.send_message.message.CopyFrom(fill_in_outgoing_message(message))
        data = await self._send_command(req)
        res = self._parse_reply(data).send_message
        return {
            "status": MessageDeliveryStatus(res.status),
            "description": res.description,
            "message_id": res.message_id.value,
            "session_id": res.session_id.value,
            "customer_id": res.customer_id.value,
        }

    async def reply_to_message(self, message_id: str, message: dict):
        """ Reply to a message from this customer """
        req = AppToServerCommand()
        req.reply_to_message.customer_id = self.customer_id
        req.reply_to_message.message_id = message_id
        req.reply_to_message.message.CopyFrom(fill_in_outgoing_message(message))
        data = await self._send_command(req)
        res = self._parse_reply(data).send_message
        return {
            "status": MessageDeliveryStatus(res.status),
            "description": res.description,
            "message_id": res.message_id.value,
            "session_id": res.session_id.value,
            "customer_id": res.customer_id.value,
        }

    async def update_activity(self, activity_channel: dict, activity: dict):
        """ Update customer's activity """
        req = AppToServerCommand()

        req.customer_activity.channel_number.number = activity_channel.get('number')
        req.customer_activity.channel_number.channel = activity_channel.get('channel', ActivityChannel.UNKNOWN).value
        req.customer_activity.customer_number.number = self.customer_number.get('number')
        req.customer_activity.customer_number.provider = self.customer_number.get('provider', CustomerNumberProvider.CELLULAR).value

        req.customer_activity.key = activity.get('key')
        req.customer_activity.session_id = activity.get('session_id')
        req.customer_activity.properties = activity.get('properties', dict())

        data = await self._send_command(req)
        res = self._parse_reply(data).customer_activity

        if not res.status:
            raise RuntimeError(res.description)

        return {
            "status": res.status,
            "description": res.description,
            "customer_id": res.customer_id.value
        }

    async def update_messaging_consent(self, messaging_channel: dict, action: MessagingConsentAction = MessagingConsentAction.ALLOW):
        """ Update customer's engagement consent on this channel """
        req = AppToServerCommand()

        req.update_messaging_consent.channel_number.number = messaging_channel.get('number')
        req.update_messaging_consent.channel_number.channel = messaging_channel.get('channel', MessagingChannel.UNKNOWN).value
        req.update_messaging_consent.customer_number.number = self.customer_number.get('number')
        req.update_messaging_consent.customer_number.provider = self.customer_number.get('provider',
                                                                                  CustomerNumberProvider.CELLULAR).value
        req.update_messaging_consent.update = action.value
        data = await self._send_command(req)
        res = self._parse_reply(data).update_messaging_consent

        return {
            "status": res.status,
            "description": res.description,
            "customer_id": res.customer_id.value
        }

    async def lease_app_data(self):
        """ Lease customer's app data """
        req = AppToServerCommand()

        if self.customer_id is not None:
            req.lease_customer_app_data.customer_id = self.customer_id
        elif self.customer_number is not None and has_key('number', self.customer_number):
            req.lease_customer_app_data.customer_number.number = self.customer_number.get('number')
            req.lease_customer_app_data.customer_number.provider = self.customer_number.get('provider',
                                                                                       CustomerNumberProvider.CELLULAR).value
        else:
            raise RuntimeError('Invalid customer id and/or customer number')

        data = await self._send_command(req)
        res = self._parse_reply(data).lease_customer_app_data

        if not res.status:
            raise RuntimeError(res.description)
        return res.value

    async def update_app_data(self, data: dict):
        """ Update customer's app data """
        req = AppToServerCommand()

        if self.customer_id is not None:
            req.update_customer_app_data.customer_id = self.customer_id
        elif self.customer_number is not None and has_key('number', self.customer_number):
            req.update_customer_app_data.customer_number.number = self.customer_number.get('number')
            req.update_customer_app_data.customer_number.provider = self.customer_number.get('provider',
                                                                                       CustomerNumberProvider.CELLULAR).value
        else:
            raise RuntimeError('Invalid customer id and/or customer number')

        req.update_customer_app_data.update.string_val = data.get('string_value')
        req.update_customer_app_data.update.bytes_val = data.get('bytes_val')
        data = await self._send_command(req)
        res = self._parse_reply(data).update_customer_app_data

        if not res.status:
            raise RuntimeError(res.description)

        return {
            "status": res.status,
            "description": res.description,
            "customer_id": res.customer_id.value
        }

    async def delete_app_data(self):
        """ Remove customer's app data """
        req = AppToServerCommand()

        if self.customer_id is not None:
            req.delete_customer_app_data.customer_id = self.customer_id
        elif self.customer_number is not None and has_key('number', self.customer_number):
            req.delete_customer_app_data.customer_number.number = self.customer_number.get('number')
            req.delete_customer_app_data.customer_number.provider = self.customer_number.get('provider',
                                                                                             CustomerNumberProvider.CELLULAR).value
        else:
            raise RuntimeError('Invalid customer id and/or customer number')

        data = await self._send_command(req)
        res = self._parse_reply(data).update_customer_app_data

        if not res.status:
            raise RuntimeError(res.description)

        return {
            "status": res.status,
            "description": res.description,
            "customer_id": res.customer_id.value
        }

    async def update_metadata(self, data: dict):
        """ Update customer's metadata """
        req = AppToServerCommand()

        if self.customer_id is not None:
            req.update_customer_metadata.customer_id = self.customer_id
        elif self.customer_number is not None and has_key('number', self.customer_number):
            req.update_customer_metadata.customer_number.number = self.customer_number.get('number')
            req.update_customer_metadata.customer_number.provider = self.customer_number.get('provider',
                                                                                             CustomerNumberProvider.CELLULAR).value
        else:
            raise RuntimeError('Invalid customer id and/or customer number')

        for key in data.keys():
            val = data.get(key)
            req.update_customer_metadata.updates[key].string_val = val.get('string_value')
            req.update_customer_metadata.updates[key].bytes_val = val.get('bytes_val')

        data = await self._send_command(req)
        res = self._parse_reply(data).update_customer_state

        if not res.status:
            raise RuntimeError(res.description)

        return {
            "status": res.status,
            "description": res.description,
            "customer_id": res.customer_id.value
        }

    async def delete_metadata(self, keys: list):
        """ Remove customer's metadata """
        req = AppToServerCommand()

        if self.customer_id is not None:
            req.delete_customer_metadata.customer_id = self.customer_id
        elif self.customer_number is not None and has_key('number', self.customer_number):
            req.delete_customer_metadata.customer_number.number = self.customer_number.get('number')
            req.delete_customer_metadata.customer_number.provider = self.customer_number.get('provider',
                                                                                             CustomerNumberProvider.CELLULAR).value
        else:
            raise RuntimeError('Invalid customer id and/or customer number')

        req.delete_customer_metadata.deletions.extend(keys)
        data = await self._send_command(req)
        res = self._parse_reply(data).update_customer_state

        if not res.status:
            raise RuntimeError(res.description)

        return {
            "status": res.status,
            "description": res.description,
            "customer_id": res.customer_id.value
        }

    async def update_secondary_ids(self, secondary_ids: list):
        """ Update customer's secondary ids """
        req = AppToServerCommand()

        if self.customer_id is not None:
            req.update_customer_secondary_id.customer_id = self.customer_id
        elif self.customer_number is not None and has_key('number', self.customer_number):
            req.update_customer_secondary_id.customer_number.number = self.customer_number.get('number')
            req.update_customer_secondary_id.customer_number.provider = self.customer_number.get('provider',
                                                                                             CustomerNumberProvider.CELLULAR).value
        else:
            raise RuntimeError('Invalid customer id and/or customer number')

        for _id in secondary_ids:
            val = CustomerIndex()
            val.mapping.key = _id.get('key')
            val.mapping.value.value = _id.get('value')
            if _id.get('expires_at') is not None:
                val.expires_at.seconds = _id.get('expires_at')
            req.update_customer_secondary_id.updates.append(val)

        data = await self._send_command(req)
        res = self._parse_reply(data).update_customer_state

        if not res.status:
            raise RuntimeError(res.description)

        return {
            "status": res.status,
            "description": res.description,
            "customer_id": res.customer_id.value
        }

    async def delete_secondary_ids(self, secondary_ids: list):
        """ Remove customer's secondary ids """
        req = AppToServerCommand()

        if self.customer_id is not None:
            req.delete_customer_secondary_id.customer_id = self.customer_id
        elif self.customer_number is not None and has_key('number', self.customer_number):
            req.delete_customer_secondary_id.customer_number.number = self.customer_number.get('number')
            req.delete_customer_secondary_id.customer_number.provider = self.customer_number.get('provider',
                                                                                                 CustomerNumberProvider.CELLULAR).value
        else:
            raise RuntimeError('Invalid customer id and/or customer number')

        for _id in secondary_ids:
            val = IndexMapping()
            val.key = _id.get('key')
            val.value.value = _id.get('value')
            req.delete_customer_secondary_id.deletions.append(val)

        data = await self._send_command(req)
        res = self._parse_reply(data).update_customer_state

        if not res.status:
            raise RuntimeError(res.description)

        return {
            "status": res.status,
            "description": res.description,
            "customer_id": res.customer_id.value
        }

    async def update_tags(self, tags: list):
        """ Update a customer's tags """
        req = AppToServerCommand()

        if self.customer_id is not None:
            req.update_customer_tag.customer_id = self.customer_id
        elif self.customer_number is not None and has_key('number', self.customer_number):
            req.update_customer_tag.customer_number.number = self.customer_number.get('number')
            req.update_customer_tag.customer_number.provider = self.customer_number.get('provider',
                                                                                                 CustomerNumberProvider.CELLULAR).value
        else:
            raise RuntimeError('Invalid customer id and/or customer number')

        for _id in tags:
            val = CustomerIndex()
            val.mapping.key = _id.get('key')
            val.mapping.value.value = _id.get('value')
            if _id.get('expires_at') is not None:
                val.expires_at.seconds = _id.get('expires_at')
            req.update_customer_tag.updates.append(val)

        data = await self._send_command(req)
        res = self._parse_reply(data).update_customer_state

        if not res.status:
            raise RuntimeError(res.description)

        return {
            "status": res.status,
            "description": res.description,
            "customer_id": res.customer_id.value
        }

    async def delete_tags(self, keys: list):
        """ Remove a customer's tags """
        req = AppToServerCommand()

        if self.customer_id is not None:
            req.delete_customer_tag.customer_id = self.customer_id
        elif self.customer_number is not None and has_key('number', self.customer_number):
            req.delete_customer_tag.customer_number.number = self.customer_number.get('number')
            req.delete_customer_tag.customer_number.provider = self.customer_number.get('provider',
                                                                                                 CustomerNumberProvider.CELLULAR).value
        else:
            raise RuntimeError('Invalid customer id and/or customer number')

        req.delete_customer_tag.deletions.extend(keys)

        data = await self._send_command(req)
        res = self._parse_reply(data).update_customer_state

        if not res.status:
            raise RuntimeError(res.description)

        return {
            "status": res.status,
            "description": res.description,
            "customer_id": res.customer_id.value
        }

    async def add_reminder(self, reminder: dict):
        """ Add a reminder """
        req = AppToServerCommand()

        if self.customer_id is not None:
            req.add_customer_reminder.customer_id = self.customer_id
        elif self.customer_number is not None and has_key('number', self.customer_number):
            req.add_customer_reminder.customer_number.number = self.customer_number.get('number')
            req.add_customer_reminder.customer_number.provider = self.customer_number.get('provider',
                                                                                        CustomerNumberProvider.CELLULAR).value
        else:
            raise RuntimeError('Invalid customer id and/or customer number')

        req.add_customer_reminder.reminder.key = reminder.get('key')
        req.add_customer_reminder.reminder.remind_at.seconds = round(reminder.get('remind_at'))
        req.add_customer_reminder.reminder.payload.value = reminder.get('payload')
        if reminder.get('interval') is not None:
            req.add_customer_reminder.reminder.interval.seconds = round(reminder.get('interval'))

        data = await self._send_command(req)
        res = self._parse_reply(data).update_customer_state

        if not res.status:
            raise RuntimeError(res.description)

        return {
            "status": res.status,
            "description": res.description,
            "customer_id": res.customer_id.value
        }

    async def cancel_reminder(self, key: str):
        """ Cancel a reminder """
        req = AppToServerCommand()

        if self.customer_id is not None:
            req.cancel_customer_reminder.customer_id = self.customer_id
        elif self.customer_number is not None and has_key('number', self.customer_number):
            req.cancel_customer_reminder.customer_number.number = self.customer_number.get('number')
            req.cancel_customer_reminder.customer_number.provider = self.customer_number.get('provider',
                                                                                          CustomerNumberProvider.CELLULAR).value
        else:
            raise RuntimeError('Invalid customer id and/or customer number')

        req.cancel_customer_reminder.key = key

        data = await self._send_command(req)
        res = self._parse_reply(data).update_customer_state

        if not res.status:
            raise RuntimeError(res.description)

        return {
            "status": res.status,
            "description": res.description,
            "customer_id": res.customer_id.value
        }

    async def _send_command(self, data):
        return await self._client._send_command(data)

    @staticmethod
    def _parse_reply(payload):
        result = AppToServerCommandReply()
        result.ParseFromString(payload.data)
        return result

