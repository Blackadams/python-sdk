import elarian

# Initialize SDK
sandbox = True
api_key = 'fake_key'
elarian_service = elarian.initialize(sandbox, api_key)

# build request
data = {
    "app_id": "fake-id",
    "customer_id": "el_cst_35ff1ebb0c11a6689e5c941723445dac-fake",
    "reminder": {
        "product_id": "fake-product-id",
        "key": "someKey",
        "expiration": {
            "seconds": 1595582280 # unix epoch
        },
        "payload": {
            "value": "Deeeeez Nuuuuts!"
        }
    }
}

req = elarian.requests.AddCustomerReminderRequest(**data)

# set reminder
resp = elarian_service.AddCustomerReminder(req)

print(resp)

