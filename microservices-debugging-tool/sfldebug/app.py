import sfldebug.messages.receive as message_receive

def run():
    """Execute the debugging application, by receiving and processing incoming messages.
    Once received, process entities associated to each message (log)
    With the collection of messages execute debugging technique
    """
    # TODO once messages are not received in MQ, add following steps
    message_receive.receive_mq()