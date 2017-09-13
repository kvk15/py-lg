#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import yaml
import socket
import paramiko
import sys

from flask import Flask
from flask import render_template
from flask import request

HOST='34bb9f10'

def parseConfig():
    config = yaml.load(open('config.yaml'))
    USER = config['user']
    PASSWORD = config['password']
    return(USER, PASSWORD);

def verip(ipaddr):
    try:
        for response in socket.getaddrinfo(ipaddr, 0):
            ip6=0
            family, socktype, proto, canonname, sockaddr = response
            if proto==6 and family==2:
                ip=sockaddr[0]
            if proto==6 and family==10:
                ip6=sockaddr[0]
    except socket.error:
        print ("<h2>Invalid IP or hostname</br>неверный Ip адрес или имя хоста</br><h2>")
        exit()
    return (ip,ip6);

def login(HOST):
    credent = parseConfig()
    USER = str(credent[0])
    PASSWORD = str(credent[1])
    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=HOST, username=USER,password=PASSWORD, allow_agent=False,look_for_keys=False)
    return ssh;
    
def summary():
    ssh = login(HOST)
    stdin, stdout, stderr = ssh.exec_command('show ip bgp summ')
    print stdout.read() + stderr.read()
    ssh.close()
    return;

def bgp(ipaddr):
    ip,ip6 = verip(ipaddr)
    ssh = login(HOST)
    stdin, stdout, stderr = ssh.exec_command("show ip bgp " + str(ip))
    print stdout.read() + stderr.read()
    ssh.close()
    return;

def best(ipaddr):
    ip,ip6 = verip(ipaddr)
    ssh = login(HOST)
    stdin, stdout, stderr = ssh.exec_command("show ip bgp " + str(ip) + " bestpath")
    print stdout.read() + stderr.read()
    ssh.close()
    return;

def advertise(ipaddr):
    ip,ip6 = verip(ipaddr)
    ssh = login(HOST)
    stdin, stdout, stderr = ssh.exec_command("show ip bgp neighbors " + str(ip) + " advertised-routes")
    print stdout.read() + stderr.read()
    ssh.close()
    return;

def trace(ipaddr):
    ip,ip6 = verip(ipaddr)
    ssh = login(HOST)
    stdin, stdout, stderr = ssh.exec_command("traceroute " + str(ipaddr))
    while not stdout.channel.exit_status_ready():
        print stdout.channel.recv(1024),
        sys.stdout.flush()
    ssh.close()
    return;

def ping(ipaddr):
    ip,ip6 = verip(ipaddr)
    ssh = login(HOST)
    stdin, stdout, stderr = ssh.exec_command("ping " + str(ipaddr))
    while not stdout.channel.exit_status_ready():
        print stdout.channel.recv(1024),
        sys.stdout.flush()
    ssh.close()
    return;

#########################################################
app = Flask(__name__)

@app.route('/')
def get_lg():
    HOST = '34bb9f10'
    IP = request.remote_addr
    return render_template('lg.html', IP=IP, hosts=HOST)

@app.route('/', methods=['GET', 'POST'])
def post_lg():
    HOST = '34bb9f10'
    IP = request.remote_addr

    if request.method == 'POST':
        if "summary" in request.form["command"]:
            result = summary()

    return render_template('lg.html', IP=IP, hosts=HOST, res=result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
