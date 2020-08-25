# Elarian Python SDK

> The wrapper provides convenient access to the Elarian APIs.

## Documentation

Take a look at the [API docs here](http://docs.elarian.com).


## Install

You can install the package from [pypi](https://pypi.org/project/elarian) by running: 

```bash
$ pip install elarian
```

## Usage


```python
import elarian

elarian_service = elarian.initialize(sandbox=True, api_key='test_api_key')

# build request
req = elarian.requests.GetCustomerStateRequest(app_id="fake-app-id", customer_id="el_cst_35f-fake")

# get customer state
resp = elarian_service.GetCustomerState(req)

print(resp)

```

## Methods

- `AuthToken()`: Generate auth token

- `GetCustomerState()`:
- `AdoptCustomerState()`: 

- `AddCustomerReminder()`:
- `AddCustomerReminderByTag()`:
- `CancelCustomerReminder()`:
- `CancelCustomerReminderByTag()`:
  
- `UpdateCustomerTag()`:
- `DeleteCustomerTag()`:

- `UpdateCustomerSecondaryId()`:
- `DeleteCustomerSecondaryId()`:

- `UpdateCustomerMetadata()`:
- `DeleteCustomerMetadata ()`:

- `SendMessage()`: Sending a message to your customer
- `SendMessageByTag()`: Sending a message to a group of customers using tags
- `ReplyToMessage()`: Replying to a message from your customer
- `MessagingConsent()`: Opting a customer in or out of receiving messages from your app

- `SendPayment()`:
- `CheckoutPayment()`:

- `MakeVoiceCall()`:
  
- `StreamNotifications()`:
- `SendWebhookResponse()`:


## Development

```bash
$ pip install grpcio grpcio-tools protobuf>=3.12.2
$ git clone --recurse-submodules https://github.com/ElarianLtd/python-sdk.git
$ cd python-sdk
$ python -m grpc_tools.protoc -I./elarian/utils/proto --python_out=./elarian/utils/generated --grpc_python_out=./elarian/utils/generated web.proto common.proto
```


Run all tests:

update the following params in your .env file then run python -m unittest discover -v

```bash
sandbox = True
api_key = 
app_id = 
product_id = 
messaging_short_code = 
```

## Issues

If you find a bug, please file an issue on [our issue tracker on GitHub](https://github.com/ElarianLtd/javascript-sdk/issues).