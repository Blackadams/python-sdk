# Elarian Python SDK

[![pypi](https://pypi.org/project/elarian)](https://pypi.org/project/elarian)

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
req = elarian.requests.GetCustomerStateRequest(org_id="fake-org-id", customer_id="el_cst_35f-fake")

# get customer state
resp = elarian_service.GetCustomerState(req)

print(resp)

```

## Methods

```
authToken(AuthTokenRequest) -> AuthTokenReply

getCustomerState(GetCustomerStateRequest) -> GetCustomerStateReply
adoptCustomerState(AdoptCustomerStateRequest) -> UpdateCustomerStateReply

addCustomerReminder(AddCustomerReminderRequest) -> UpdateCustomerStateReply
addCustomerReminderByTag(AddCustomerReminderTagRequest) -> TagCommandReply
cancelCustomerReminder(CancelCustomerReminderRequest) -> UpdateCustomerStateReply
cancelCustomerReminderByTag(CancelCustomerReminderTagRequest) -> TagCommandReply

updateCustomerTag(UpdateCustomerTagRequest) -> UpdateCustomerStateReply
deleteCustomerTag(DeleteCustomerTagRequest) -> UpdateCustomerStateReply

updateCustomerSecondaryId(UpdateCustomerSecondaryIdRequest) -> UpdateCustomerStateReply
deleteCustomerSecondaryId(DeleteCustomerSecondaryIdRequest) -> UpdateCustomerStateReply

leaseCustomerMetadata(LeaseCustomerMetadataRequest) -> LeaseCustomerMetadataReply
updateCustomerMetadata(UpdateCustomerMetadataRequest) -> UpdateCustomerStateReply
deleteCustomerMetadata(DeleteCustomerMetadataRequest) -> UpdateCustomerStateReply

sendMessage(SendMessageRequest) -> SendMessageReply
sendMessageByTag(SendMessageTagRequest) -> TagCommandReply
replyToMessage(ReplyToMessageRequest) -> SendMessageReply
messagingConsent(MessagingConsentRequest) -> MessagingConsentReply

sendPayment(SendPaymentRequest) -> InitiatePaymentReply
checkoutPayment(CheckoutPaymentRequest) -> InitiatePaymentReply
customerWalletPayment(CustomerWalletPaymentRequest) -> InitiatePaymentReply

makeVoiceCall(MakeVoiceCallRequest) -> MakeVoiceCallReply

streamNotifications(StreamNotificationRequest) -> WebhookRequest
sendWebhookResponse(WebhookResponse) -> WebhookResponseReply
```


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