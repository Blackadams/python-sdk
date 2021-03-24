from elarian.client import Client
from elarian.utils.generated.app_socket_pb2 import AppToServerCommand, AppToServerCommandReply, GenerateAuthTokenCommand


class Elarian(Client):

    def __init__(self, org_id, api_key, app_id, options=Client.default_options):
        super().__init__(
            org_id,
            api_key,
            app_id,
            [
                'reminder',
                'messagingSessionStarted',
                'messagingSessionRenewed',
                'messagingSessionEnded',
                'messagingConsentUpdate'
                'receivedSms',
                'receivedFbMessenger',
                'receivedTelegram',
                'receivedWhatsapp',
                'receivedEmail',
                'voiceCall',
                'ussdSession',
                'messageStatus',
                'sentMessageReaction',
                'receivedPayment',
                'paymentStatus',
                'walletPaymentStatus',
                'customerActivity'
            ],
            options,
        )

    @staticmethod
    def _parse_reply(payload):
        result = AppToServerCommandReply()
        result.ParseFromString(payload.data)
        return result

    async def generate_auth_token(self):
        req = AppToServerCommand()
        req.generate_auth_token.CopyFrom(GenerateAuthTokenCommand())
        data = await self._send_command(req)
        res = self._parse_reply(data).generate_auth_token
        return {
            "token": res.token,
            "lifetime": res.lifetime.seconds
        }

