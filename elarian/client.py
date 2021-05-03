
import ssl
import asyncio
import atexit
from abc import ABCMeta
from rsocket import Payload, RSocket
from elarian.utils.generated.app_socket_pb2 import AppConnectionMetadata
from elarian.utils.request_handler import _RequestHandler


class Client(metaclass=ABCMeta):
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
    _loop = None
    _request_handler = _RequestHandler(None)

    def __init__(self, org_id: str, api_key: str, app_id: str, events: list, options: dict = None):
        self._app_id = app_id
        self._api_key = api_key
        self._org_id = org_id
        self._expected_events = events + ['pending', 'error', 'connecting', 'connected', 'closed']
        if options is not None:
            self._options.update(options)

    async def connect(self):
        """ Connect to Elarian """
        self._request_handler.handle("pending")

        setup = AppConnectionMetadata()
        setup.org_id = self._org_id
        setup.app_id = self._app_id
        setup.api_key.value = self._api_key
        setup.simplex_mode = not self._options['allow_notifications']
        setup.simulator_mode = self._is_simulator

        self._loop = asyncio.get_event_loop()
        self._connection = await asyncio.open_connection(
            host='tcp.elarian.dev',
            loop=self._loop,
            port=8082,
            ssl=ssl.create_default_context(),
            server_hostname='tcp.elarian.dev',
        )
        self._socket = RSocket(
            reader=self._connection[0],
            writer=self._connection[1],
            server=False,
            loop=self._loop,
            data_encoding=b'application/octet-stream',
            metadata_encoding=b'application/octet-stream',
            setup_payload=Payload(data=setup.SerializeToString()),
            keep_alive_milliseconds=self._options['keep_alive'],
            max_lifetime_milliseconds=self._options['lifetime'],
            handler_factory=self._make_request_handler,
            error_handler=self._error_handler
        )

        self._is_connected = True
        self._loop.create_task(self.__keep_running())

        self._request_handler.handle("connected")
        atexit.register(self.__clean_up)

        return self

    async def disconnect(self):
        """ Disconnect from Elarian """
        self._is_connected = False
        self._connection[1].close()
        await self._socket.close()
        self._request_handler.handle("closed")

    def is_connected(self):
        return self._is_connected

    def set_on_connection_pending(self, handler):
        return self._on('pending', handler)

    def set_on_connection_error(self, handler):
        return self._on('error', handler)

    def set_on_connection_closed(self, handler):
        return self._on('closed', handler)

    def set_on_connecting(self, handler):
        return self._on('connecting', handler)

    def set_on_connected(self, handler):
        return self._on('connected', handler)

    def _on(self, event, handler):
        if event in self._expected_events:
            self._request_handler.register_handler(event, handler)
        else:
            raise RuntimeError("Unexpected event {0}. Must be one of {1}".format(event, self._expected_events))
        return self

    def _make_request_handler(self, socket):
        registered = self._request_handler.get_handlers()
        self._request_handler = _RequestHandler(socket)
        self._request_handler._is_simulator = self._is_simulator
        for event in registered.keys():
            self._request_handler.register_handler(event, registered[event])
        self._request_handler.handle("connecting")
        return self._request_handler

    def _error_handler(self, error: Payload):
        self._request_handler.handle("error", RuntimeError(error.data.decode()))
        self._loop.create_task(self.disconnect())

    def __clean_up(self):
        if self.is_connected():
            if self._loop.is_running():
                self._loop.create_task(self.disconnect())
            else:
                asyncio.run(self.disconnect())

    async def __keep_running(self):
        while self.is_connected():
            await asyncio.sleep(2)

    async def _send_command(self, data):
        if not self.is_connected():
            raise RuntimeError("Client is not connected")
        return await self._socket.request_response(self._make_payload(data))

    @staticmethod
    def _make_payload(data):
        return Payload(data=data.SerializeToString())
