from io import BlockingIOError
from _socket import error as SocketError

class Connection():

    def __init__(self, socket, channel):
        """
        :param socket: The Socket for this connection to listen on
        :param channel: management channel
        :return:
        """
        self.socket = socket
        self.channel = channel
        self.connection_id = None
        self.connection = None
        self.is_connected = False

    def start(self, connection_id):
        """
        :param connection_id: the identifier for this connection
        :return:
        """
        print("Connection Thread # : {cnum} starting up.".format(cnum=connection_id))
        self.connection = self.connect()
        self.connection_id = connection_id
        self.listen_for_data()

    def connect(self):
        """
        Checks to see if someone is looking to connect.
        :return: returns the socket connection
        """
        try:
            conn, addr = self.socket.accept()
            self.connection = conn
            print("Trying to connect")
            self.channel.send('start')
            self.is_connected = True
            return conn
        except (BlockingIOError, SocketError) as e:
            self.channel.send("None")

    def disconnect(self):
        """
        Ends the connection with the client by sending a message to the manager.
        :return:
        """
        print("disconnecting")
        self.connection = None
        self.is_connected = False
        self.channel.send("{id} disconnecting".format(id=self.connection_id))

    def listen_for_data(self):
        """
        Non blocking listener.
        :return:
        """
        if self.connection:
            try:
                data = self.connection.recv(1024)
                if data:
                    print("Connection {id} Received {data}".format(id=self.connection_id, data=data))
                    self.channel.send("ID {id} DATA: {data} END".format(id=self.connection_id, data=data))
            except BlockingIOError:
                print(" No data found, continue")
                pass
            except:
                print("Unknown Error, dropping connection {id}".format(id=self.connection_id))
                self.disconnect()
                raise

    def send(self, data):
        """
        Returns data to the server
        :param data: data to send
        :return:
        """
        print("Sending {data}".format(data=data))
        data = data.encode('utf-8')
        self.connection.sendall(data)


