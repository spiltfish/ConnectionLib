# ConnectionLib
A little socked connection manager for servers

To start running:

def run(self):
 self.connection_manager = ConnectionManager()
 self.connection_manager.start_accepting_connections()
 print("Connection Manager is now Accepting New Connections")
 while True:
  self.connection_manager.manage_connections()
  stackless.run()
