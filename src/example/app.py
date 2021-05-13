import os
import time
import traceback
import asyncio
from elarian import Elarian

sms_channel = {
    'number': os.getenv('SMS_SHORT_CODE'),
    'channel': 'SMS'
}

voice_channel = {
    'number': os.getenv('VOICE_NUMBER'),
    'channel': 'VOICE'
}

mpesa_channel = {
    'number': os.getenv('MPESA_PAYBILL'),
    'channel': 'CELLULAR'
}

purse_id = os.getenv('PURSE_ID')

client = Elarian(
    org_id=os.getenv('ORG_ID'),
    app_id=os.getenv('APP_ID'),
    api_key=os.getenv('API_KEY'),
)


async def approve_loan(customer, amount):
    try:
        print(f"Approving loan for {customer.customer_number['number']}")
        meta = await customer.get_metadata()
        name = meta['name']
        repayment_date = time.time() + 60
        res = await client.initiate_payment(
            debit_party={
                'purse': {
                    'purse_id': purse_id
                }
            },
            credit_party={
                'customer': {
                    'channel_number': mpesa_channel,
                    'customer_number': customer.customer_number
                }
            },
            value={
                'amount': amount,
                'currency_code': 'KES'
            }
        )

        if res['status'] != 'SUCCESS' or res['status'] != 'PENDING_CONFIRMATION':
            raise RuntimeError(f"Failed to make payment {res}")

        await customer.update_metadata({
            'name': name,
            'balance': amount,
        })

        await customer.send_message(messaging_channel=sms_channel, message={
            'body': {
                "text": f"Congratulations {name}!\nYour loan of KES {amount} has been approved!\nYou are expected to pay it back by {repayment_date}"
            }
        })

        await customer.add_reminder({
            'key': 'moni',
            'remind_at': repayment_date,
            'payload': '',
        })

    except Exception as ex:
        print(f"Failed to approve payment {ex}")
        traceback.print_exc()


async def handle_payment(notif, customer, app_data, callback):
    try:
        print(f"Processing payment from {customer.customer_number['number']}")
        amount = notif['value']['amount']
        meta = await customer.get_metadata()
        name = meta.get('name', 'Unknown Customer')
        balance = float(meta.get('balance', 0))

        new_balance = balance - amount
        await customer.update_metadata({
            'name': name,
            'balance': new_balance,
        })

        if new_balance <= 0:
            text = f"Thank you for your payment {name}, your loan has been fully repaid!!"
            await customer.cancel_reminder('moni')
            await customer.delete_metadata(['name', 'strike', 'balance', 'screen'])
        else:
            text = f"Hey {name}!\nThank you for your payment, but you still owe me KES ${new_balance}"

        await customer.send_message(messaging_channel=sms_channel, message={
            'body': {
                "text": text
            }
        })

    except Exception as ex:
        print(f"Failed to handle payment {ex}")
        traceback.print_exc()


async def handle_ussd(notif, customer, app_data, callback):
    try:
        print(f"Processing ussd from {customer.customer_number['number']}")
        ussd_input = notif['input']
        screen = app_data.get('screen', 'home')

        meta = await customer.get_metadata()
        name = meta.get('name', None)
        balance = meta.get('balance', 0)

        menu = {
            "text": None,
            "is_terminal": False
        }

        next_screen = screen
        if screen == 'home' and ussd_input != '':
            if ussd_input == '1':
                next_screen = 'request-name'
            elif ussd_input == '2':
                next_screen = 'quit'

        if screen == 'home' and ussd_input == '':
            if name is not None:
                next_screen = 'info'

        if next_screen == 'quit':
            menu['text'] = 'Happy Coding!'
            menu['is_terminal'] = True
            next_screen = 'home'
            callback({"body": {"ussd": menu}}, {"screen": next_screen})

        elif next_screen == 'info':
            menu['text'] = f"Hey {name}, "
            menu['text'] += f"you still owe me KES {balance}" if balance > 0 else "you have repaid your loan, good for you!"
            menu['is_terminal'] = True
            next_screen = 'home'
            callback({"body": {"ussd": menu}}, {"screen": next_screen})

        elif next_screen == 'request-name':
            menu['text'] = "Alright, what is your name?"
            next_screen = 'request-amount'
            callback({"body": {"ussd": menu}}, {"screen": next_screen})

        elif next_screen == 'request-amount':
            name = ussd_input
            menu['text'] = f"Okay {name}, how much do you need?"
            next_screen = 'approve-amount'
            callback({"body": {"ussd": menu}}, {"screen": next_screen})

        elif next_screen == 'approve-amount':
            balance = float(ussd_input)
            menu['text'] = f"Awesome! {name} we are reviewing your application and will be in touch shortly!\nHave a lovely day!"
            menu['is_terminal'] = True
            next_screen = 'home'
            callback({"body": {"ussd": menu}}, {"screen": next_screen})
            await approve_loan(customer, balance)

        elif next_screen == 'home':
            menu['text'] = "Welcome to MoniMoni!\n1. Apply for loan\n2. Quit"
            menu['is_terminal'] = False
            callback({"body": {"ussd": menu}}, {"screen": next_screen})

        await customer.update_metadata({"name": name, "balance": balance})
    except Exception as ex:
        print(f"Failed to process ussd {ex}")
        traceback.print_exc()


async def handle_reminder(notif, customer, app_data, callback):
    try:
        print(f"Processing reminder for {customer.customer_number['number']}")
        meta = await customer.get_metadata()
        name = meta['name']
        balance = meta['balance']
        strike = meta.get('strike', 1)

        channel = sms_channel
        message = {
            "body": {
                "text": f"Hello {name}, this is a friendly reminder to pay back my KES {balance}"
            }
        }
        if strike == 2:
            message['body']['text'] = f"Hey {name}, you still need to pay back my KES {balance}"
        elif strike > 2:
            channel = voice_channel
            message['body'] = {
                "voice": [
                    {
                        "say": {
                            "text": f"Yo ${name}! You need to pay back my KES {balance}",
                            "voice": "male"
                        }
                    }
                ]
            }
        await customer.send_message(messaging_channel=channel, message=message)
        meta['strike'] = strike + 1
        await customer.update_metadata(meta)

        reminder = {"key": "moni", "remind_at": time.time() + 60, "payload": ''}
        await customer.add_reminder(reminder)

    except Exception as ex:
        print(f"Failed to process reminder {ex}")


async def start():
    client.set_on_ussd_session(handle_ussd)
    client.set_on_reminder(handle_reminder)
    client.set_on_received_payment(handle_payment)
    client.set_on_connection_error(lambda err: print(f"{err}"))
    client.set_on_connection_closed(lambda: print(f"Connection Closed"))
    client.set_on_connected(lambda: print(f"App is connected, waiting for customers on {os.getenv('USSD_CODE')}"))
    await client.connect()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start())
    loop.run_forever()
