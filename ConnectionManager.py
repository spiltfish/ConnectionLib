import stackless
from Connection import Connection
import socket
from settings import HOST, PORT, MAX_USERS
import Queue
from exceptions import ConnectionNotFoundException


class ConnectionManager:

    def __init__(self):
        self.connections = []
        self.unused_connections = []
        self.connection_channel = stackless.channel()
        self.socket = self._set_up_socket()
        self.num_users = 0
        self.start_new_c = False
        self.accept_new_connections = False
        self.outbound_message_queue = Queue.Queue()
        self.inbound_message_queue = Queue.Queue()

    def queue_outbound_message(self, message):
        """
        Adds a message, waiting to be sent.
        :param message: a Message object
        :return:
        """
        self.outbound_message_queue.put(message)

    def get_inbound_message_queue(self):
        """
        :return: Queue Object containing all new messages.
        """
        return self.inbound_message_queue

    def start_accepting_connections(self):
        """
        Allows the server to start accepting connections.
        :return:
        """
        self.accept_new_connections = True
        stackless.tasklet(self.connection_channel.send)('start')
        self._listen_to_connections()
        self._reply_to_connections()

    def manage_connections(self):
        """
        Checks if there are any clients connecting or disconnecting
        Then listens for new data coming in from clients
        Then sends out messages
        :return:
        """
        channel_message = self.connection_channel.receive()
        if "start" in channel_message:
            self.num_users += 1
            stackless.tasklet(self._start_new_connection)(self.num_users)
        if "disconnecting" in channel_message:
            self._disconnect(channel_message)
        self._listen_to_connections()
        self._reply_to_connections()

    def _listen_to_connections(self):
        """
        Has each connection look for data on the line
        :return:
        """
        for connection in self.connections:
            if connection.is_connected:
                stackless.tasklet(connection.listen_for_data)()
            else:
                stackless.tasklet(connection.connect)()

    def _reply_to_connections(self):
        """
        sends any queues messages
        :return:
        """
        while not self.outbound_message_queue.empty():
            stackless.tasklet(self._send_message)

    def _disconnect(self, channel_message):
        """
        Stops listening to a connection.
        :param channel_message: Message send determining which connection to kill
        :return:
        """
        connection_id = int(channel_message.split(" ")[0])
        for connection in self.connections:
            if connection.connection_id == connection_id:
                self.connections.remove(connection)
                print(self.connections)

    def _start_new_connection(self, connection_id):
        """
        Starts up a new connection thread to wait for a new client to connect
        :param connection_id: identified for the connection object
        :return:
        """
        print("start_new_connection")
        connection = Connection(self.socket, self.connection_channel)
        self.connections.append(connection)
        connection.start(connection_id)

    def _set_up_socket(self):
        """
        Sets up the socket to use for communication. Listens on all IPs
        :return:
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setblocking(0)
        s.bind((HOST, PORT))
        s.listen(2)
        return s

    def _send_message(self):
        """
        sends a message from the queue.
        :return:
        """
        message = self.outbound_message_queue.get()
        if self.connections.get(message.client_id):
            connection = self.connections[message.client_id]
            connection.send(message.message_body)
        else:
            print("No connection with id {id}".format(id=message.client_id))



if __name__ == '__main__':
    conn_manager = ConnectionManager()
    conn_manager.start_accepting_connections()

