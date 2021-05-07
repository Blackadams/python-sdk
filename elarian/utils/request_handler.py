import asyncio
import json
import traceback
from rsocket import Payload, BaseRequestHandler
from elarian.customer import Customer
from google.protobuf.json_format import MessageToJson
from elarian.utils.generated.messaging_model_pb2 import MessagingChannel
from elarian.utils.generated.app_socket_pb2 import AppConnectionMetadata,\
    ServerToAppNotification,\
    ServerToAppNotificationReply
from elarian.utils.generated.simulator_socket_pb2 import ServerToSimulatorNotification,\
    ServerToSimulatorNotificationReply
from elarian.utils.helpers import fill_in_outgoing_message


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
        print("No handler for notification:", notif)
        callback(data_update=app_data, response=None)

    async def request_response(self, payload: Payload) -> asyncio.Future:
        future = asyncio.Future()
        try:
            data = ServerToSimulatorNotification() if self._is_simulator else ServerToAppNotification()
            data.ParseFromString(payload.data)

            if data.WhichOneof("entry") == 'customer':
                data = data.customer
            elif data.WhichOneof("entry") == 'purse':
                data = data.purse

            event = data.WhichOneof("entry")
            notif = getattr(data, event)

            customer = None
            app_data = data.app_data if data.HasField('app_data') else None
            app_data = None if app_data is None else json.loads(
                MessageToJson(message=app_data, preserving_proto_field_name=True))
            data = json.loads(MessageToJson(message=data, preserving_proto_field_name=True))
            notif = json.loads(MessageToJson(message=notif, preserving_proto_field_name=True))

            customer_number = None
            if event == 'received_message':
                customer_number = notif['customer_number']
                channel = MessagingChannel.Value(notif['channel_number']['channel'])
                if channel is MessagingChannel.MESSAGING_CHANNEL_SMS:
                    event = 'received_sms'
                    notif['text'] = notif['parts'][0]['text']
                if channel is MessagingChannel.MESSAGING_CHANNEL_VOICE:
                    event = 'voice_call'
                if channel is MessagingChannel.MESSAGING_CHANNEL_USSD:
                    event = 'ussd_session'
                    notif['input'] = notif['parts'][0]['ussd']
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

            if not self._is_simulator:
                customer = Customer(client=self._client, id=data['customer_id'])
                if customer_number is not None:
                    customer = Customer(
                        client=self._client,
                        id=data['customer_id'],
                        number=customer_number['number'],
                        provider=customer_number['provider'])

                # FIXME: Format notification data
                notif['org_id'] = data['org_id']
                notif['app_id'] = data['app_id']
                notif['customer_id'] = customer.customer_id
                notif['created_at'] = data['created_at']

            def callback(response=None, data_update=None):
                res = ServerToSimulatorNotificationReply() if self._is_simulator else ServerToAppNotificationReply()
                if not self._is_simulator:
                    print("In callback:", response)
                    if response is not None:
                        res.message.CopyFrom(fill_in_outgoing_message(response))
                    if data_update is not None:
                        res.data_update.update.string_val = data_update.get("string_value")
                        res.data_update.update.bytes_val = data_update.get("bytes_val")
                    print(res)
                future.set_result(Payload(data=res.SerializeToString()))

            if asyncio.iscoroutinefunction(handler):
                await handler(notif, customer, app_data, callback)
            else:
                handler(notif, customer, app_data, callback)
        except Exception as ex:
            traceback.print_exc()
            future.set_exception(ex)

        return future

