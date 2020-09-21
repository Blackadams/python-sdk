from .service import Elarian
import elarian.utils.generated.web_pb2 as requests

__version__ = "0.0.0"

def initialize(api_key, auth_token=None):
    return Elarian(api_key, auth_token)