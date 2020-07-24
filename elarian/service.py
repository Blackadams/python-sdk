import sys
import grpc
from grpc import metadata_call_credentials, ssl_channel_credentials, composite_channel_credentials

from .utils.auth import GenerateCallCredentials
from .utils.generated import web_pb2_grpc, web_pb2
    

PRODUCTION_HOST = 'api.elarian.com:443'
SANDBOX_HOST = 'api.elarian.dev:443'

def Elarian(sandbox, api_key, auth_token):
    if not api_key and not auth_token:
        raise RuntimeError('Either one of apiKey or authToken is required')

    host = SANDBOX_HOST if sandbox == True else PRODUCTION_HOST

    ssl_credentials = ssl_channel_credentials()
    call_credentials = metadata_call_credentials(GenerateCallCredentials(api_key, auth_token))
    channel_credentials = composite_channel_credentials(ssl_credentials, call_credentials)
    
    channel = grpc.secure_channel(host, channel_credentials, options=[('grpc.keepalive_timeout_ms', 15000)])

    try:
        grpc.channel_ready_future(channel).result(timeout=10)
    except grpc.FutureTimeoutError:
        sys.exit('Error connecting to server')
    else:
        stub = web_pb2_grpc.GrpcWebServiceStub(channel)      
    
    return stub
