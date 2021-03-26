from .client import Client
from elarian.utils.generated.simulator_socket_pb2 import \
    SimulatorToServerCommand,\
    SimulatorToServerCommandReply
from elarian.utils.generated.messaging_model_pb2 import \
    InboundMessageBody
from elarian.utils.helpers import has_key
from elarian.models import *


class Simulator(Client):
    """..."""
    def __init__(self, org_id, api_key, app_id, options=Client.default_options):
        super().__init__(
            org_id,
            api_key,
            app_id,
            [
                'send_message',
                'make_voice_call',
                'send_customer_payment',
                'send_channel_payment',
                'checkout_payment'
            ],
            options,
        )
        self._is_simulator = True

    def set_on_send_message(self, handler):
        return self._on('send_message', handler)

    def set_on_make_voice_call(self, handler):
        return self._on('make_voice_call', handler)

    def set_on_send_customer_payment(self, handler):
        return self._on('send_customer_payment', handler)

    def set_on_send_channel_payment(self, handler):
        return self._on('send_channel_payment', handler)

    def set_on_checkout_payment(self, handler):
        return self._on('checkout_payment', handler)

    async def receive_message(self, phone_number: str, messaging_channel: dict, session_id: str, message_parts: list):
        """..."""
        req = SimulatorToServerCommand()
        req.receive_message.session_id.value = session_id
        req.receive_message.customer_number = phone_number
        req.receive_message.channel_number.number = messaging_channel['number']
        req.receive_message.channel_number.channel = messaging_channel['channel'].value

        parts = req.receive_message.parts
        for part in message_parts:
            _part = InboundMessageBody()

            if has_key('text', part):
                _part.text = part['text']

            if has_key('ussd', part):
                _part.ussd.value = part['ussd']

            if has_key('media', part):
                _part.media.url = part['media']['url']
                _part.media.media = part['media']['type'].value

            if has_key('location', part):
                _part.location.latitude = part['location']['latitude']
                _part.location.longitude = part['location']['longitude']
                _part.location.label.value = part['location']['label']
                _part.location.address.value = part['location']['address']

            if has_key('email', part):
                _part.email.subject = part['email']['subject']
                _part.email.body_plain = part['email']['plain']
                _part.email.body_html = part['email']['html']
                _part.email.cc_list.extend(part['email']['cc'])
                _part.email.bcc_list.extend(part['email']['bcc'])
                _part.email.attachments.extend(part['email']['attachments'])

            if has_key('voice', part):
                _part.voice.direction = part['voice']['direction'].value
                _part.voice.status = part['voice']['status'].value
                _part.voice.started_at.seconds = part['voice']['started_at']
                _part.voice.hangup_cause = part['voice']['hangup_cause'].value
                _part.voice.dtmf_digits.value = part['voice']['dtmf_digits']
                _part.voice.recording_url.value = part['voice']['recording_url']

                _part.voice.dial_data.destination_number = part['voice']['dial_data']['destination_number']
                _part.voice.dial_data.started_at.seconds = part['voice']['dial_data']['started_at']
                _part.voice.dial_data.duration.seconds = part['voice']['dial_data']['duration']

                _part.voice.queue_data.enqueued_at.seconds = part['voice']['queue_data']['enqueued_at']
                _part.voice.queue_data.dequeued_at.seconds = part['voice']['queue_data']['dequeued_at']
                _part.voice.queue_data.dequeued_to_number.value = part['voice']['queue_data']['dequeued_to_number']
                _part.voice.queue_data.dequeued_to_sessionId.value = part['voice']['queue_data']['dequeued_to_sessionId']
                _part.voice.queue_data.queue_duration.seconds = part['voice']['queue_data']['queue_duration']

            parts.append(_part)

        data = await self._send_command(req)
        res = self._parse_reply(data)
        return {
            "status": res.status,
            "description": res.description,
            "message": res.message
        }

    async def receive_payment(self,
                              phone_number: str,
                              payment_channel: dict,
                              transaction_id: str,
                              value: dict,
                              status: PaymentStatus):
        """..."""
        req = SimulatorToServerCommand()
        req.receive_payment.transaction_id = transaction_id
        req.receive_payment.customer_number = phone_number
        req.receive_payment.status = status.value
        req.receive_payment.value.amount = value['amount']
        req.receive_payment.value.currency_code = value['currency_code']
        req.receive_payment.channel_number.number = payment_channel['number']
        req.receive_payment.channel_number.channel = payment_channel['channel'].value

        data = await self._send_command(req)
        res = self._parse_reply(data)
        return {
            "status": res.status,
            "description": res.description,
            "message": res.message
        }

    async def update_payment_status(self, transaction_id: str, status: PaymentStatus):
        """..."""
        req = SimulatorToServerCommand()
        req.update_payment_status.transaction_id = transaction_id
        req.update_payment_status.status = status.value

        data = await self._send_command(req)
        res = self._parse_reply(data)
        return {
            "status": res.status,
            "description": res.description,
            "message": res.message
        }

    @staticmethod
    def _parse_reply(payload):
        result = SimulatorToServerCommandReply()
        result.ParseFromString(payload.data)
        return result

