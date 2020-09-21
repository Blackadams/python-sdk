import elarian
import unittest

from . import api_key, messaging_short_code, app_id, product_id

elarian_service = elarian.initialize(api_key)

class TestSendSms(unittest.TestCase):
    def test_send_sms(self):       
        data = {
            "customer_number": {
                "provider": "CUSTOMER_NUMBER_PROVIDER_TELCO",
                "number": "+254712345678"
            },
            "body": {
                "text": {
                    "text": { "value": "the world is yours"}
                }
            },
            "channel_number": {
                "channel": "MESSAGING_CHANNEL_SMS",
                "number": messaging_short_code
            },
            "app_id": app_id,
            "product_id": product_id
        } 
    
        req = elarian.requests.SendMessageRequest(**data)
        resp = elarian_service.SendMessage(req)

        assert resp.description == 'The message has been sent'



if __name__ == '__main__':
    unittest.main()