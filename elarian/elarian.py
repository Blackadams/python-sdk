from elarian.client import Client
from elarian.models import PaymentStatus
from elarian.utils.helpers import fill_in_outgoing_message, has_key
from elarian.utils.generated.app_socket_pb2 import (
    AppToServerCommand,
    AppToServerCommandReply,
    GenerateAuthTokenCommand,
)
from .utils.generated.common_model_pb2 import (
    CustomerIndex,
    ChannelNumberProvider,
    CustomerNumberProvider,
)
from .utils.generated.payment_model_pb2 import (
    PaymentChannel,
)
from .utils.helpers import get_provider


class Elarian(Client):
    """..."""

    def __init__(self, org_id, api_key, app_id, options=Client.default_options):
        super().__init__(
            org_id,
            api_key,
            app_id,
            [
                "reminder",
                "messaging_session_started",
                "messaging_session_renewed",
                "messaging_session_ended",
                "messaging_consent_update" "received_sms",
                "received_fb_messenger",
                "received_telegram",
                "received_whatsapp",
                "received_email",
                "voice_call",
                "ussd_session",
                "message_status",
                "sent_message_reaction",
                "received_payment",
                "payment_status",
                "wallet_payment_status",
                "customer_activity",
            ],
            options,
        )

    def set_on_reminder(self, handler):
        """Used to set the handler functionon setting a reminder"""
        return self._on("reminder", handler)

    def set_on_messaging_session_started(self, handler):
        """Used to set the handler function on starting a messaging session"""
        return self._on("messaging_session_started", handler)

    def set_on_messaging_session_renewed(self, handler):
        """Used to set the handler function on renewing a messaging session"""
        return self._on("messaging_session_renewed", handler)

    def set_on_messaging_session_ended(self, handler):
        """Used to set the handler function on ending a messaging session"""
        return self._on("messaging_session_ended", handler)

    def set_on_messaging_consent_update(self, handler):
        """Used to set the handler function on updating the message consent"""
        return self._on("messaging_consent_update", handler)

    def set_on_received_sms(self, handler):
        """Used to set the handler function on receiving an sms"""
        return self._on("received_sms", handler)

    def set_on_received_fb_messenger(self, handler):
        """Used to set the handler function on receiving an fb message"""
        return self._on("received_fb_messenger", handler)

    def set_on_received_telegram(self, handler):
        """Used to set the handler function on receiving a telegram message"""
        return self._on("received_telegram", handler)

    def set_on_received_whatsapp(self, handler):
        """Used to set the handler function on receiving a whatsapp message"""
        return self._on("received_whatsapp", handler)

    def set_on_received_email(self, handler):
        """Used to set the handler function on receiving an email"""
        return self._on("received_email", handler)

    def set_on_voice_call(self, handler):
        """Used to set the handler function on creating a voice call"""
        return self._on("voice_call", handler)

    def set_on_ussd_session(self, handler):
        """Used to set the handler function on creating a USSD session"""
        return self._on("ussd_session", handler)

    def set_on_message_status(self, handler):
        """Used to set the handler function on message status"""
        return self._on("message_status", handler)

    def set_on_sent_message_reaction(self, handler):
        """Used to set the handler function on message reaction"""
        return self._on("sent_message_reaction", handler)

    def set_on_received_payment(self, handler):
        """Used to set the handler function on receiving a payment"""
        return self._on("received_payment", handler)

    def set_on_payment_status(self, handler):
        """Used to set the handler function on receiving payment status"""
        return self._on("payment_status", handler)

    def set_on_wallet_payment_status(self, handler):
        """Used to set the handler function on getting wallet payment status"""
        return self._on("wallet_payment_status", handler)

    def set_on_customer_activity(self, handler):
        """Used to set the handler function on getting customer activity"""
        return self._on("customer_activity", handler)

    async def generate_auth_token(self):
        """Used to generate an auth token """
        req = AppToServerCommand()
        req.generate_auth_token.CopyFrom(GenerateAuthTokenCommand())
        data = await self._send_command(req)
        res = self._parse_reply(data).generate_auth_token
        return {"token": res.token, "lifetime": res.lifetime.seconds}

    async def add_customer_reminder_by_tag(self, tag: dict, reminder: dict):
        """Used to set a reminder to be triggered at the specified time for customers with a particular tag"""
        req = AppToServerCommand()
        req.add_customer_reminder_tag.tag.key = tag["key"]
        req.add_customer_reminder_tag.tag.value.value = tag["value"]
        req.add_customer_reminder_tag.reminder.key = reminder["key"]
        req.add_customer_reminder_tag.reminder.remind_at.seconds = round(
            reminder["remind_at"]
        )
        if has_key("interval", reminder):
            req.add_customer_reminder_tag.reminder.interval.seconds = round(
                reminder["interval"]
            )
        req.add_customer_reminder_tag.reminder.payload.value = reminder["payload"]
        data = await self._send_command(req)
        res = self._parse_reply(data).tag_command
        if not res.status:
            raise RuntimeError(res.description)
        return {
            "status": res.status,
            "description": res.description,
            "work_id": res.work_id.value,
        }

    async def cancel_customer_reminder_by_tag(self, tag: dict, reminder_key: str):
        """Used to cancela a previously set reminder using a tag and key """
        req = AppToServerCommand()
        req.cancel_customer_reminder_tag.key = reminder_key
        req.cancel_customer_reminder_tag.tag.key = tag["key"]
        req.cancel_customer_reminder_tag.tag.value.value = tag["value"]
        data = await self._send_command(req)
        res = self._parse_reply(data).tag_command
        if not res.status:
            raise RuntimeError(res.description)
        return {
            "status": res.status,
            "description": res.description,
            "work_id": res.work_id.value,
        }

    async def send_message_by_tag(
        self, tag: dict, messaging_channel: dict, message: dict
    ):
        """Used to send a message by a specific tag"""
        req = AppToServerCommand()
        req.send_message_tag.channel_number.number = messaging_channel["number"]
        req.send_message_tag.channel_number.channel = messaging_channel["channel"].value
        req.send_message_tag.tag.key = tag["key"]
        req.send_message_tag.tag.value.value = tag["value"]
        req.send_message_tag.message.CopyFrom(fill_in_outgoing_message(message))
        data = await self._send_command(req)
        res = self._parse_reply(data).tag_command
        if not res.status:
            raise RuntimeError(res.description)
        return {
            "status": res.status,
            "description": res.description,
            "work_id": res.work_id.value,
        }

    async def initiate_payment(
        self, debit_party: dict, credit_party: dict, value: dict
    ):
        """Used to initiate a payment transaction"""
        req = AppToServerCommand()

        if has_key("purse", debit_party):
            req.initiate_payment.debit_party.purse.purse_id = debit_party["purse"]["purse_id"]
        elif has_key("customer", debit_party):
            req.initiate_payment.debit_party.customer.customer_number.number = (
                debit_party["customer"]["customer_number"]["number"]
            )
            req.initiate_payment.debit_party.customer.customer_number.provider = get_provider(
                CustomerNumberProvider,
                debit_party["customer"]["customer_number"]["provider"],
                "CUSTOMER_NUMBER_PROVIDER",
            )
            if has_key("partition", debit_party["customer"]["customer_number"]):
                req.initiate_payment.debit_party.customer.customer_number.partition = (
                    debit_party["customer"]["customer_number"]["partition"]
                )
            req.initiate_payment.debit_party.customer.channel_number.number = (
                debit_party["customer"]["channel_number"]["number"]
            )
            req.initiate_payment.debit_party.customer.channel_number.channel = get_provider(
                PaymentChannel,
                debit_party["customer"]["channel_number"]["channel"],
                "PAYMENT_CHANNEL",
            )
        elif has_key("wallet", debit_party):
            req.initiate_payment.debit_party.wallet.wallet_id = debit_party["wallet"]["wallet_id"]
            req.initiate_payment.debit_party.wallet.customer_id = debit_party["wallet"]["customer_id"]
        elif has_key("channel", debit_party):
            req.initiate_payment.debit_party.channel.channel_number.number = (
                debit_party["channel"]["channel_number"]["number"]
            )
            req.initiate_payment.debit_party.channel.channel_number.channel = get_provider(
                PaymentChannel,
                debit_party["customer"]["channel_number"]["channel"],
                "PAYMENT_CHANNEL",
            )
            req.initiate_payment.debit_party.channel.channel_code = debit_party["channel"]["network_code"]
            req.initiate_payment.debit_party.channel.account.value = debit_party["channel"]["account"].value

        if has_key("purse", credit_party):
            req.initiate_payment.credit_party.purse.purse_id = credit_party["purse"][
                "purse_id"
            ]
        elif has_key("customer", credit_party):
            req.initiate_payment.credit_party.customer.customer_number.number = (
                credit_party["customer"]["customer_number"]["number"]
            )
            req.initiate_payment.credit_party.customer.customer_number.provider = get_provider(
                CustomerNumberProvider,
                credit_party["customer"]["customer_number"]["provider"],
                "CUSTOMER_NUMBER_PROVIDER",
            )
            if has_key("partition", credit_party["customer"]["customer_number"]):
                req.initiate_payment.credit_party.customer.customer_number.partition = (
                    credit_party["customer"]["customer_number"]["partition"]
                )
            req.initiate_payment.credit_party.customer.channel_number.number = (
                credit_party["customer"]["channel_number"]["number"]
            )
            req.initiate_payment.credit_party.customer.channel_number.channel = get_provider(
                PaymentChannel,
                credit_party["customer"]["channel_number"]["channel"],
                "PAYMENT_CHANNEL",
            )
        elif has_key("wallet", credit_party):
            req.initiate_payment.credit_party.wallet.wallet_id = credit_party["wallet"][
                "wallet_id"
            ]
            req.initiate_payment.credit_party.wallet.customer_id = credit_party["wallet"]["customer_id"]
        elif has_key("channel", credit_party):
            req.initiate_payment.credit_party.channel.channel_number.number = (
                credit_party["channel"]["channel_number"]["number"]
            )
            req.initiate_payment.credit_party.channel.channel_number.channel = get_provider(
                PaymentChannel,
                credit_party["customer"]["channel_number"]["channel"],
                "PAYMENT_CHANNEL",
            )
            req.initiate_payment.credit_party.channel.channel_code = credit_party[
                "channel"
            ]["network_code"]
            req.initiate_payment.credit_party.channel.account.value = credit_party[
                "channel"
            ]["account"].value

        req.initiate_payment.value.amount = value["amount"]
        req.initiate_payment.value.currency_code = value["currency_code"]
        data = await self._send_command(req)
        res = self._parse_reply(data).initiate_payment
        return {
            "status": PaymentStatus(res.status),
            "description": res.description,
            "transaction_id": res.transaction_id.value,
            "debit_customer_id": res.debit_customer_id.value,
            "credit_customer_id": res.credit_customer_id.value,
        }

    @staticmethod
    def _parse_reply(payload):
        result = AppToServerCommandReply()
        result.ParseFromString(payload.data)
        return result
