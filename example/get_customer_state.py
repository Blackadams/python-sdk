import elarian

# Initialize SDK
sandbox = True
api_key = 'fake_key'
elarian_service = elarian.initialize(sandbox, api_key)

# build request
req = elarian.requests.GetCustomerStateRequest(
    app_id="fake-app-id", 
    customer_id="el_cst_35ff1ebb0c11a6689e5c941723445dac-fake"
)

# get customer state
resp = elarian_service.GetCustomerState(req)

print(resp)
