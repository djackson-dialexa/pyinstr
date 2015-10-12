#!/usr/bin/env python2.7

import SocketServer
import visa
import json

class InstrumentManager:
    def __init__(self):
        self.instruments = {}
        self.rm = visa.ResourceManager()

    def list_instruments(self):
        return self.rm.list_resources()

    def open_instrument(self, identifier):
        if identifier in self.instruments.keys():
            return self.instruments[identifier]
        else:
            instr = self.rm.open_resource(identifier)
            self.instruments[identifier] = instr
            return instr

    def query_instrument(self, identifier, query):
        instr = self.open_instrument(identifier)
        return instr.query(query)

insman = InstumentManager()

class InstrumentRequestHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        line = self.rfile.readline().strip()
        command = line.split(' ')[0]
        if command == 'list':
            self.wfile.write(json.dumps(self.list_instruments())+'\r\n')
        elif command == 'open':
            identifier = line.split(' ')[1]
            self.wfile.write(json.dumps(self.open_instrument(identifier))+'\r\n')
        elif command == 'query':
            identifier = line.split(' ')[1]
            query = ' '.join(line.split(' ')[2:])
            self.wfile.write(json.dumps(self.query_instrument(identifier))+'\r\n')

    def list_instruments(self):
        return insman.list_resources()

    def open_instrument(self, identifier):
        return insman.open_instrument(identifier)

    def query_instrument(self, identifier, query):
        return insman.query_instrument(identifier, query)


if __name__ == '__main__':
    HOST, PORT = "0.0.0.0", 9090

    server = SocketServer.TCPServer((HOST, PORT), InstrumentRequestHandler)

    server.serve_forever()
