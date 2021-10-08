#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2021 Ze Hui Peng https://github.com/zhpeng811/
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
from urllib.parse import urlparse # https://docs.python.org/3.6/library/urllib.html
from urllib.error import HTTPError

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

        url_info = {
            "path": parse_result.path if parse_result.path != '' else '/',
            "host": parse_result.hostname,
            # default port number will be port 80
            "port": parse_result.port if parse_result.port else 80
        }

        return url_info

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def construct_payload(self, url_info, command, args=None):
        '''
        Construct the payload information for requests
        GET request payload source: https://reqbin.com/req/nfilsyk5/get-request-example
        
        Args:
            url_info: the URL information returned from parse_url()
            command: the type of request, either "GET" or "POST"
        Returns:
            A string that requests the request payload
        '''
        if (command == "GET"):
            # format idea from: https://stackoverflow.com/a/54950733
            return (
                f'GET {url_info.get("path")} HTTP/1.1\r\n'
                f'Host: {url_info.get("host")}\r\n'
                'Connection: close\r\n'
                'Accept: */*\r\n\r\n'
            )
        elif (command == "POST"):
            content = ''
            if (args):
                for (key, value) in args.items():
                    content += f"{key}={value}&"
                # remove the last '&' character
                content = content[:-1]

            return (
                f'POST {url_info.get("path")} HTTP/1.1\r\n'
                f'Host: {url_info.get("host")}\r\n'
                'Connection: close\r\n'
                'Content-Type: application/x-www-form-urlencoded\r\n'
                f'Content-Length: {len(content)}\r\n\r\n'
                f'{content}\r\n\r\n'
            )

    def parse_response(self, data):
        """
        Parse the response and extract the headers, body, and status code 
        """
        parse_data = data.split("\r\n\r\n")
        response = {
            'headers': parse_data[0],
            'body': parse_data[1],
            'code': int(parse_data[0].split('\r\n')[0].split()[1])
        }
        return response

    def get_code(self, data):
        '''
        This function will be redirected to the parse_response function
        This function is kept for potential reference in the unit tests
        '''
        return self.parse_response(data)['code']

    def get_headers(self, data):
        '''
        This function will be redirected to the parse_response function
        This function is kept for potential reference in the unit tests
        '''
        return self.parse_response(data)['headers']

    def get_body(self, data):
        return self.parse_response(data)['body']
    
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

    def handle_request(self, command, url, args=None):
        '''
        Handles both the GET and POST requests
         
        Args:
            command: the request command, should be either "GET" or "POST"
            url: the URL of the request
            args: any additional parameters to the request
        '''
        url_info = self.parse_url(url)

        # connect to the client, send the request, and receive the response
        print(url_info)
        self.connect(url_info.get("host"), url_info.get("port"))
        payload = self.construct_payload(url_info, command, args)
        self.sendall(payload)
        data = self.recvall(self.socket)
        self.close()

        response = self.parse_response(data)
        code = response['code']
        body = response['body']

        # user story: As a user when I GET or POST I want the result printed to stdout
        print(f"response status code: {code}")
        print(f"response body: {body}")
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
