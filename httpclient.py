#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2023 Sankalp Saini
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
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        port = urllib.parse.urlparse(url).port
        host_extra_path = urllib.parse.urlparse(url).path
        if port is None:
            port = 80
        if not host_extra_path:
            host_extra_path = "/"
        hostname = urllib.parse.urlparse(url).hostname
        return hostname, port, host_extra_path

    def connect(self, host, port):
        # Connect to socket with specified host and port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = data.split(" ")[1]
        return int(code)

    # Don't believe this was needed
    def get_headers(self,data):
        return None

    def get_body(self, data):
        data_list = data.split('\r\n\r\n')
        body = data_list[1]
        return body
    
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

    def GET(self, url, args=None):
        hostname, port, host_extra_path = self.get_host_port(url)

        self.connect(hostname, port)

        message = "GET "+host_extra_path+" HTTP/1.1\r\nHost: " + hostname + "\r\nConnection: close\r\n\r\n"

        self.sendall(message)

        response = self.recvall(self.socket)

        # get the code and body
        code = self.get_code(response)
        body = self.get_body(response)

        print("HTTP Code: " + str(code) + '\nBody Message: ' + body)

        self.close()
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        hostname, port, host_extra_path = self.get_host_port(url)

        self.connect(hostname, port)

        if args:
            args = urllib.parse.urlencode(args)
            content_length = str(len(args))
        else:
            content_length = "0"

        if not args:
            message = "POST "+host_extra_path+" HTTP/1.1\r\nHost: "+hostname+"\r\nContent-Type: application/x-www-form-urlencoded\r\nUser-Agent:Linux\r\nContent-Length: "+content_length+"\r\nConnection: close\r\n\r\n"
        else:
            message = "POST "+host_extra_path+" HTTP/1.1\r\nHost: "+hostname+"\r\nContent-Type: application/x-www-form-urlencoded\r\nUser-Agent:Linux\r\nContent-Length: "+content_length+"\r\nConnection: close\r\n\r\n"+args+"\r\n\r\n"
        self.sendall(message)

        response = self.recvall(self.socket)

        # get the code and body
        code = self.get_code(response)
        body = self.get_body(response)

        print("HTTP Code: " + str(code) + '\nBody Message: ' + body)

        self.close()

        return HTTPResponse(code, body)

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
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command( sys.argv[1] ))