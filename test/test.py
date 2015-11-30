#! /usr/bin/pypy

from ConnectionManager import ConnectionManager
import stackless


class Server:

    def __init__(self):
        self.connection_manager = None
        self.logger = None

    def run(self):
        print("Server Starting Up.")
        self.connection_manager = ConnectionManager()
        print("Connection Manager Started")
        self.connection_manager.start_accepting_connections()
        print("Connection Manager is now Accepting New Connections")
        while True:
            self.connection_manager.manage_connections()
            stackless.run()


if __name__ == "__main__":
    server = Server()
    server.run()
