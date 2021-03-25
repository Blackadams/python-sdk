from .client import Client


class Simulator(Client):
    """..."""
    def __init__(self, org_id, api_key, app_id, options):
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
        self.is_simulator = True

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
        pass

    async def receive_payment(self, phone_number: str, payment_channel: dict, transaction_id: str, value: list, status: int):
        """..."""
        pass

    async def update_payment_status(self, transaction_id: str, status: int):
        """..."""
        pass

