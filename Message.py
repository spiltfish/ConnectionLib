class Message:
    """
    Simple message class for constructing communications to/from clients
    """

    def __init__(self, client_id, message_body):
        self.client_id = client_id
        self.message_body = message_body
