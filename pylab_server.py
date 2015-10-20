#!/usr/bin/env python2.7

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import visa
import json
import base64
import cgi

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

    def query_instrument_binary(self, identifier, query):
        instr = self.open_instrument(identifier)
        return instr.query_binary_values(query, datatype='B', is_big_endian=True)

    def write_instrument(self, identifier, query):
        instr = self.open_instrument(identifier)
        instr.write(query)
        return "OK"


insman = InstrumentManager()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

#class InstrumentRequestHandler(SocketServer.StreamRequestHandler):
#    def handle(self):
#        line = self.rfile.readline().strip()
#        command = line.split(' ')[0]
#        if command == 'list':
#            self.wfile.write(json.dumps(self.list_instruments())+'\r\n')
#        elif command == 'open':
#            identifier = line.split(' ')[1]
#            self.wfile.write(json.dumps(self.open_instrument(identifier))+'\r\n')
#        elif command == 'write':
#            identifier = line.split(' ')[1]
#            query = ' '.join(line.split(' ')[2:])
#            self.wfile.write(json.dumps(self.write_instrument(identifier, query))+'\r\n')
#        elif command == 'query':
#            identifier = line.split(' ')[1]
#            query = ' '.join(line.split(' ')[2:])
#            self.wfile.write(json.dumps(self.query_instrument(identifier, query))+'\r\n')
#        elif command == 'queryb':
#            identifier = line.split(' ')[1]
#            query = ' '.join(line.split(' ')[2:])
#            self.wfile.write(json.dumps(self.query_instrument_binary(identifier, query))+'\r\n')
#
#    def list_instruments(self):
#        return insman.list_instruments()
#
#    def open_instrument(self, identifier):
#        return insman.open_instrument(identifier)
#
#    def write_instrument(self, identifier, query):
#        return insman.write_instrument(identifier, query)
#
#    def query_instrument(self, identifier, query):
#        return insman.query_instrument(identifier, query).strip()
#
#    def query_instrument_binary(self, identifier, query):
#        return base64.b64encode(insman.query_instrument_binary(identifier, query))


class InstrumentRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        response_code = 200
        content_type = 'application/json'
        content = ""
        try:
            path_elements = [x for x in self.path.split('/') if x]
            if len(path_elements) > 0:
                if path_elements[0] in insman.list_instruments():
                    content = json.dumps({'response': insman.query_instrument(path_elements[0], '*IDN?')})
            else:
                content = json.dumps({'instruments': insman.list_instruments()})    
        except Exception, e:
            response_code = 500
        finally:
            self.send_response(response_code)
            self.send_header("Content-type", content_type)
            self.end_headers()
            if content:
                self.wfile.write(content)

    def do_POST(self):
        response_code = 200
        content_type = 'application/json'
        content = ""
        try:
            path_elements = [x for x in self.path.split('/') if x]
            if len(path_elements) > 0:
                if path_elements[0] in insman.list_instruments():
                    ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                    print ctype
                    print pdict
                    if ctype == 'multipart/form-data':
                        postvars = cgi.parse_multipart(self.rfile, pdict)
                    elif ctype == 'application/x-www-form-urlencoded':
                        length = int(self.headers.getheader('content-length'))
                        postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
                    else:
                        postvars = {}
                    print postvars
                    if postvars['type'] == 'query':
                        content = json.dumps({'response': insman.query_instrument(path_elements[0], postvars['query'])})
            else:
                content = json.dumps({})    
        except Exception, e:
            response_code = 500
        finally:
            self.send_response(response_code)
            self.send_header("Content-type", content_type)
            self.end_headers()
            if content:
                self.wfile.write(content)


if __name__ == '__main__':
    HOST, PORT = "0.0.0.0", 9090

    server = ThreadedHTTPServer((HOST, PORT), InstrumentRequestHandler)
    server.serve_forever()
