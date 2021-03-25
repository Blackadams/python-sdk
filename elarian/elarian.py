from elarian.client import Client
from elarian.utils.generated.app_socket_pb2 import AppToServerCommand, AppToServerCommandReply, GenerateAuthTokenCommand


class Elarian(Client):
    """..."""
    def __init__(self, org_id, api_key, app_id, options=Client.default_options):
        super().__init__(
            org_id,
            api_key,
            app_id,
            [
                'reminder',
                'messaging_session_started',
                'messaging_session_renewed',
                'messaging_session_ended',
                'messaging_consent_update'
                'received_sms',
                'received_fb_messenger',
                'received_telegram',
                'received_whatsapp',
                'received_email',
                'voice_call',
                'ussd_session',
                'message_status',
                'sent_message_reaction',
                'received_payment',
                'payment_status',
                'wallet_payment_status',
                'customer_activity'
            ],
            options,
        )

    def set_on_reminder(self, handler):
        return self._on('reminder', handler)

    def set_on_messaging_session_started(self, handler):
        return self._on('messaging_session_started', handler)

    def set_on_messaging_session_renewed(self, handler):
        return self._on('messaging_session_renewed', handler)

    def set_on_messaging_session_ended(self, handler):
        return self._on('messaging_session_ended', handler)

    def set_on_messaging_consent_update(self, handler):
        return self._on('messaging_consent_update', handler)

    def set_on_received_sms(self, handler):
        return self._on('received_sms', handler)

    def set_on_received_fb_messenger(self, handler):
        return self._on('received_fb_messenger', handler)

    def set_on_received_telegram(self, handler):
        return self._on('received_telegram', handler)

    def set_on_received_whatsapp(self, handler):
        return self._on('received_whatsapp', handler)

    def set_on_received_email(self, handler):
        return self._on('received_email', handler)

    def set_on_voice_call(self, handler):
        return self._on('voice_call', handler)

    def set_on_ussd_session(self, handler):
        return self._on('ussd_session', handler)

    def set_on_message_status(self, handler):
        return self._on('message_status', handler)

    def set_on_sent_message_reaction(self, handler):
        return self._on('sent_message_reaction', handler)

    def set_on_received_payment(self, handler):
        return self._on('received_payment', handler)

    def set_on_payment_status(self, handler):
        return self._on('payment_status', handler)

    def set_on_wallet_payment_status(self, handler):
        return self._on('wallet_payment_status', handler)

    def set_on_customer_activity(self, handler):
        return self._on('customer_activity', handler)

    async def generate_auth_token(self):
        """ Generate auth token """
        req = AppToServerCommand()
        req.generate_auth_token.CopyFrom(GenerateAuthTokenCommand())
        data = await self._send_command(req)
        res = self._parse_reply(data).generate_auth_token
        return {
            "token": res.token,
            "lifetime": res.lifetime.seconds
        }

    async def add_customer_reminder_by_tag(self, tag: dict, reminder: dict):
        """ Set a reminder to be triggered at the specified time for customers with the particular tag """
        pass

    async def cancel_customer_reminder_by_tag(self, tag: dict, reminder_key: str):
        """ Cancels a previously set reminder with tag and key """
        pass

    async def send_message_by_tag(self, tag: dict, message: dict):
        """ Send a message by tag """
        pass

    async def initiate_payment(self, debit_party: dict, credit_party: dict, value: dict):
        """ Initiate a payment transaction """
        pass

    @staticmethod
    def _parse_reply(payload):
        result = AppToServerCommandReply()
        result.ParseFromString(payload.data)
        return result

