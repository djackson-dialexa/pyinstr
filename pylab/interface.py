import socket
import sys
import json
import base64

class Interface:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send_command(self, command):
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        received = None

        try:
            sck.connect((self.host, self.port))
            sck.sendall(command+"\r\n")

            received = sck.recv(8192)
            print received
        finally:
            sck.close()

        return received

    def list_instruments(self):
        return json.loads(self.send_command("list"))

    def query(self, instr_id, query):
        return json.loads(self.send_command("query %s %s" % (instr_id, query)))

    def query_binary(self, instr_id, query):
        return base64.b64decode(json.loads(self.send_command("queryb %s %s" % (instr_id, query))))

    def write(self, instr_id, query):
        return self.send_command("query %s %s" % (instr_id, query))
