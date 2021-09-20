#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2021 Ze Hui Peng
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket # https://docs.python.org/3.6/library/socket.html
import re
from inspect import cleandoc
from urllib.parse import urlparse # https://docs.python.org/3.6/library/urllib.html

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def parse_url(self, url):
        '''
        Parse the url using the urllib library
        There are three useful attributes that will be retrived from the result
        
        Returns:
            A dict that contains the following key-value pairs:
                path: Hierachical path (str)
                hostname: Host name in lowercase (str)
                port: Port number (int)
        '''
        parse_result = urlparse(url)

        # TODO: ask for clairification regarding requests without http://
        url_info = {
            "path": parse_result.path,
            "host": parse_result.hostname,
            # default port number will be port 80
            "port": parse_result.port if parse_result.port else 80
        }

        return url_info

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def construct_payload(self, url_info, command):
        '''
        Construct the payload information for requests
        GET request payload source: https://reqbin.com/req/nfilsyk5/get-request-example
        
        Returns:
        A string that requests the request payload
        '''
        if (command == "GET"):
            return "GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n".format(url_info.get("path"), url_info.get("host"))
        elif (command == "POST"):
            return f'''
            POST 
            '''

    # def parse_response(self, data):

    def get_code(self, data):
        return None

    def get_headers(self, data):
        return None

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def handle_request(self, type, url, args=None):
        url_info = self.parse_url(url)

        # connect to the client, send the request, and receive the response
        self.connect(url_info.get("host"), url_info.get("port"))
        payload = self.construct_payload(url_info, "GET")
        print(payload)
        self.sendall(payload)
        data = self.recvall(self.socket)
        print(data)
        code = 500
        body = ""
        return HTTPResponse(code, body)

    def GET(self, url, args=None):
        '''
        This function will be redirected to the handle_request function
        This function have to be kept for passing the unit tests
        '''
        return self.handle_request("GET", url, args)

    def POST(self, url, args=None):
        '''
        This function will be redirected to the handle_request function
        This function have to be kept for passing the unit tests
        '''
        return self.handle_request("POST", url, args)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
