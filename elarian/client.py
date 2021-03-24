
import ssl
import asyncio

from rsocket import Payload, RSocket, BaseRequestHandler
from elarian.utils.generated.app_socket_pb2 import AppConnectionMetadata


class _RequestHandler(BaseRequestHandler):
    def request_response(self, payload: Payload) -> asyncio.Future:
        future = asyncio.Future()
        future.set_exception(RuntimeError("Not implemented"))
        return future


class Client:
    default_options = {
        "resumable": False,
        "lifetime": 60000,
        "keep_alive": 1000,
        "allow_notifications": True,
    }

    _org_id = None
    _app_id = None
    _api_key = None
    _is_simulator = False
    _options = default_options

    _socket = None
    _connection = None
    _is_connected = False

    def __init__(self, org_id: str, api_key: str, app_id: str, options: dict = None):
        self._app_id = app_id
        self._api_key = api_key
        self._org_id = org_id
        if options is not None:
            self._options = options

    async def connect(self):
        setup = AppConnectionMetadata()
        setup.org_id = self._org_id
        setup.app_id = self._app_id
        setup.api_key.value = self._api_key
        setup.simplex_mode = not self._options['allow_notifications']
        setup.simulator_mode = self._is_simulator

        self._connection = await asyncio.open_connection(
            host='tcp.elarian.dev',
            port=8082,
            ssl=ssl.create_default_context(),
            server_hostname='tcp.elarian.dev',
        )
        self._socket = RSocket(
            reader=self._connection[0],
            writer=self._connection[1],
            server=False,
            loop=asyncio.get_event_loop(),
            data_encoding=b'application/octet-stream',
            metadata_encoding=b'application/octet-stream',
            setup_payload=Payload(data=setup.SerializeToString()),
            keep_alive_milliseconds=self._options['keep_alive'],
            max_lifetime_milliseconds=self._options['lifetime'],
            handler_factory=_RequestHandler,
            error_handler=self._error_handler
        )
        self._is_connected = True
        return self

    async def disconnect(self):
        await self._socket.close()

    def is_connected(self):
        return self._is_connected

    def _error_handler(self, error: Payload):
        print("Connection Error", error)
        self._is_connected = False
        self._connection[1].close()
        loop = asyncio.get_event_loop()
        loop.create_task(self._socket.close())

    async def _send_command(self, data):
        if not self.is_connected():
            raise RuntimeError("Client is not connected")
        return await self._socket.request_response(self._make_payload(data))

    @staticmethod
    def _make_payload(data):
        return Payload(data=data.SerializeToString())
