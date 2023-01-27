#  coding: utf-8 
import socketserver
from os import path as op

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Copyright 2023 Junhyeon Cho
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html

# This file has been modified by Junhyeon Cho
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    # HTTP METHOD status code 
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
    nl = "\r\n"
    enc = "utf-8"
    
    def create_response(self, status_code, param):
        status_dict = {
            200: ['OK', f'Content-Type: text/{param[0]}', self.nl + param[1]],
            301: ['Moved Permanently', f'Location: {param[0]}/', ''],
            400: ['Bad Request', self.nl],
            404: ['Not Found', self.nl],
            405: ['Method Not Allowed', self.nl]
        }
        return f"HTTP/1.1 {status_code} " + self.nl.join(status_dict[status_code])
    
    def respond(self, status_code, param = ['', '']):
        self.request.sendall(bytearray(self.create_response(status_code, param), self.enc))
        
    def resolve_path(self, path):
        if path == '/': return path
        current = ''
        last_slash = 0
        paths = [each for each in path.split('/')[1:]]
        for each in paths:
            if each == '..':
                if last_slash == 0:
                    raise Exception()
                current = current[0:last_slash+1]
                last_slash = len(current) - current[::-1].index('/') - 1
            current += '/' + each
        
        return current
        
        
    def handle(self):
        ACCEPTED_REQUEST = ['GET']
        self.data = self.request.recv(1024).strip()
        
        # Converting bytes to string
        # https://stackoverflow.com/questions/606191/convert-bytes-to-a-string
        sdata = self.data.decode(self.enc)
        
        if not sdata:
            self.respond(400)
            return
        
        ldata = sdata.split(self.nl)
        lheader = ldata[0].split()
        http_method= lheader[0]
        if http_method not in ACCEPTED_REQUEST:
            self.respond(405)
            return
            
        try:
            path = self.resolve_path(lheader[1])
        except Exception:
            self.respond(404)
            return
            
        original_path = '' + path
        path = './www'+path
        
        if not op.exists(path):
            self.respond(404)
            return
            
        def get_text(fp):
            with open(fp) as f:
                return f.read()
        
        if op.isdir(path):
            if path[-1] != '/':
                self.respond(301, [original_path, ''])
                return
            
            path += 'index.html'
            text = get_text(path)
            
            if text is None or text == '':
                self.respond(404)
                return
            
            self.respond(200, ['html', text])
            return
        
        text = get_text(path)
        
        if text is None or text == '':
            self.respond(404)
            return
        
        for filetype in ['html', 'css']:
            # checking file type
            # https://stackoverflow.com/questions/5899497/how-can-i-check-the-extension-of-a-file
            if op.splitext(path)[-1].lower() == ('.' + filetype):
                self.respond(200, [filetype, text])
                return
            
        # unexpected filetype requested, thus reject
        self.respond(404)
        return

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
