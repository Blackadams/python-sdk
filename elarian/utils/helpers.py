from .generated.common_model_pb2 import CustomerNumber
from .generated.messaging_model_pb2 import OutboundMessage,\
    VoiceCallAction,\
    RecordSessionCallAction,\
    RejectCallAction


def has_key(key: str, data: dict):
    return key in data.keys()


def fill_in_outgoing_message(message: dict):
    _message = OutboundMessage()
    _message.labels.extend(message.get('labels', []))
    _message.provider_tag.value = message['provider_tag']
    _message.reply_token.value = message['reply_token']
    _message.reply_prompt.action = message['reply_prompt']['action'].value
    _message.reply_prompt.menu.extend(message['reply_prompt']['menu'])

    body = message['body']

    if has_key('text', body):
        _message.body.text = body['text']

    if has_key('url', body):
        _message.body.url = body['url']

    if has_key('ussd', body):
        _message.body.ussd.text = body['ussd']['text']
        _message.body.ussd.is_terminal = body['ussd']['is_terminal']

    if has_key('media', body):
        _message.body.media.url = body['media']['url']
        _message.body.media.media = body['media']['type'].value

    if has_key('location', body):
        _message.body.location.latitude = body['location']['latitude']
        _message.body.location.longitude = body['location']['longitude']
        _message.body.location.label.value = body['location']['label']
        _message.body.location.address.value = body['location']['address']

    if has_key('template', body):
        _message.body.template.id = body['template']['id']
        _message.body.template.params = body['template']['params']

    if has_key('email', body):
        _message.body.email.subject = body['email']['subject']
        _message.body.email.body_plain = body['email']['plain']
        _message.body.email.body_html = body['email']['html']
        _message.body.email.cc_list.extend(body['email']['cc'])
        _message.body.email.bcc_list.extend(body['email']['bcc'])
        _message.body.email.attachments.extend(body['email']['attachments'])

    if has_key('voice', body):
        for action in body['voice']:
            _action = VoiceCallAction()

            if has_key('say', action):
                _action.say.text = action['say']['text']
                _action.say.play_beep = action['say']['play_beep']
                _action.say.voice = action['say']['voice'].value

            if has_key('play', action):
                _action.play.url = action['play']['url']

            if has_key('get_digits', action):
                _action.get_digits.num_digits.value = action['get_digits']['num_digits']
                _action.get_digits.timeout.seconds = action['get_digits']['timeout']
                _action.get_digits.finish_on_key.value = action['get_digits']['finish_on_key']

                if has_key('say', action.get_digits):
                    _action.get_digits.say.text = action['get_digits']['say']['text']
                    _action.get_digits.say.play_beep = action['get_digits']['say']['play_beep']
                    _action.get_digits.say.voice = action['get_digits']['say']['voice'].value

                if has_key('play', action.get_digits):
                    _action.get_digits.play.url = action['get_digits']['play']['url']

            if has_key('get_recording', action):
                _action.get_recording.timeout.seconds = action['get_recording']['timeout']
                _action.get_recording.max_length.seconds = action['get_recording']['max_length']
                _action.get_recording.finish_on_key.value = action['get_recording']['finish_on_key']
                _action.get_recording.play_beep = action['get_recording']['play_beep']
                _action.get_recording.trim_silence = action['get_recording']['trim_silence']

                if has_key('say', action.get_recording):
                    _action.get_recording.say.text = action['get_recording']['say']['text']
                    _action.get_recording.say.play_beep = action['get_recording']['say']['play_beep']
                    _action.get_recording.say.voice = action['get_recording']['say']['voice'].value

                if has_key('play', action.get_recording):
                    _action.get_recording.play.url = action['get_recording']['play']['url']

            if has_key('dial', action):
                _action.dial.record = action['dial']['record']
                _action.dial.sequential = action['dial']['sequential']
                _action.dial.ringback_tone.value = action['dial']['ringback_tone']
                _action.dial.caller_id.value = action['dial']['caller_id']
                _action.dial.max_duration.value = action['dial']['max_duration']
                numbers = []
                for num in action['dial']['customer_numbers']:
                    _num = CustomerNumber()
                    _num.number = num['number']
                    _num.provider = num['provider'].value
                    _num.partition.value = num['partition']
                    numbers.append(num)
                _action.dial.customer_numbers.extend(numbers)

            if has_key('record_session', action):
                _action.record_session.CopyFrom(RecordSessionCallAction())

            if has_key('enqueue', action):
                _action.enqueue.hold_music.value = action['enqueue']['hold_music']
                _action.enqueue.queue_name.value = action['enqueue']['queue_name']

            if has_key('dequeue', action):
                _action.dequeue.record = action['dequeue']['record']
                _action.dequeue.queue_name.value = action['dequeue']['queue_name']
                _action.dequeue.channel_number.number = action['dequeue']['channel']['number']
                _action.dequeue.channel_number.channel = action['dequeue']['channel']['channel'].value

            if has_key('reject', action):
                _action.reject.CopyFrom(RejectCallAction())

            if has_key('redirect', action):
                _action.redirect.url = action['redirect']['url']

            _message.body.voice.actions.append(_action)

    return _message
