import asyncio
from rsocket import Payload, BaseRequestHandler
from elarian.customer import Customer
from elarian.utils.generated.messaging_model_pb2 import MessagingChannel
from elarian.utils.generated.app_socket_pb2 import AppConnectionMetadata,\
    ServerToAppNotification,\
    ServerToAppNotificationReply
from elarian.utils.generated.simulator_socket_pb2 import ServerToSimulatorNotification,\
    ServerToSimulatorNotificationReply


class _RequestHandler(BaseRequestHandler):
    _handlers = dict()
    _is_simulator = False
    _client = None

    def register_handler(self, event, handler):
        self._handlers[event] = handler

    def handle(self, event, *args):
        if event in self._handlers.keys():
            handler = self._handlers[event]
            if asyncio.iscoroutinefunction(handler):
                loop = asyncio.get_event_loop()
                loop.create_task(handler(*args))
            else:
                handler(*args)

    def get_handlers(self):
        return self._handlers

    @staticmethod
    async def _default_handler(notif, customer, app_data, callback):
        print(notif, customer, app_data)
        callback(data_update=app_data, response=None)

    async def request_response(self, payload: Payload) -> asyncio.Future:
        future = asyncio.Future()
        data = ServerToSimulatorNotification() if self._is_simulator else ServerToAppNotification()
        data.ParseFromString(payload.data)
        event = data.WhichOneof("entry")
        notif = data[event]

        customer_number = None
        if event == 'received_message':
            customer_number = notif.customer_number
            channel = notif.channel_number.channel
            if channel is MessagingChannel.MESSAGING_CHANNEL_SMS:
                event = 'received_sms'
            if channel is MessagingChannel.MESSAGING_CHANNEL_VOICE:
                event = 'voice_call'
            if channel is MessagingChannel.MESSAGING_CHANNEL_USSD:
                event = 'ussd_session'
            if channel is MessagingChannel.MESSAGING_CHANNEL_FB_MESSENGER:
                event = 'received_fb_messenger'
            if channel is MessagingChannel.MESSAGING_CHANNEL_TELEGRAM:
                event = 'received_telegram'
            if channel is MessagingChannel.MESSAGING_CHANNEL_WHATSAPP:
                event = 'received_whatsapp'
            if channel is MessagingChannel.MESSAGING_CHANNEL_EMAIL:
                event = 'received_email'

        if event in self._handlers.keys():
            handler = self._handlers[event]
        else:
            handler = self._default_handler

        if self._is_simulator:  # ServerToSimulator
            app_data = None
            customer = None
        else:  # ServerToApp
            app_data = data.app_data
            customer = Customer(client=self._client, id=data.customer_id)
            if customer_number is not None:
                customer = Customer(
                    client=self._client,
                    id=data.customer_id,
                    number=customer_number.number,
                    provider=customer_number.provider)
            # FIXME: Format notification data
            notif['org_id'] = data.org_id
            notif['app_id'] = data.app_id
            notif['customer_id'] = customer.customer_id
            notif['created_at'] = data.created_at.seconds

        def callback(response, data_update):
            res = ServerToSimulatorNotificationReply() if self._is_simulator else ServerToAppNotificationReply()
            if not self._is_simulator:
                res.data_update = data_update
                res.message = response  # FIXME: Format response properly for voice and ussd
            future.set_result(Payload(data=res.SerializeToString()))

        if asyncio.iscoroutinefunction(handler):
            await handler(notif, customer, app_data, callback)
        else:
            handler(notif, customer, app_data, callback)

        return future

