import elarian

# Initialize SDK
sandbox = True
api_key = 'fake_key'
elarian_service = elarian.initialize(sandbox, api_key)

# build request
data = {
        "customer_number": {
            "provider": "CUSTOMER_NUMBER_PROVIDER_TELCO",
            "number": "+254711276275"
        },
        "body": {
            "text": {
                "text": { "value": "the world is yours"}
            }
        },
        "channel_number": {
            "channel": "MESSAGING_CHANNEL_SMS",
            "number": "41012" # replace with your shortcode
        },
        "app_id": "app-j80HNf", # replace with your app id
        "product_id": "product-j80HNf" # replace with your product id
    } 

req = elarian.requests.SendMessageRequest(**data)

# send sms
resp = elarian_service.SendMessage(req)

print(resp)
