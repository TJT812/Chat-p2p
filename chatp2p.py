import socket
from datetime import datetime
import ipaddress
import subprocess
import threading
import select
import queue
import time
import os

PORT = 9999
BUFFER = 2048




def getADDR():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    res = s.getsockname()[0]
    s.close()
    return res

def getNETMASK(ip):
    proc = subprocess.Popen('ipconfig',stdout=subprocess.PIPE)
    while True:
        line = proc.stdout.readline()
        if ip.encode() in line:
            break
    mask = proc.stdout.readline().rstrip().split(b':')[-1].replace(b' ',b'').decode()
    return mask




IP = getADDR()
MASK = getNETMASK(IP)

host = ipaddress.IPv4Address(IP)
net = ipaddress.IPv4Network(IP + '/' + MASK, False)
print('IP:', IP)
print('Mask:', MASK)
print('Subnet:', ipaddress.IPv4Address(int(host) & int(net.netmask)))
print('Host:', ipaddress.IPv4Address(int(host) & int(net.hostmask)))
print('Broadcast:', net.broadcast_address)



peers = []
messages = []
def udp_first_connection(name):
    global peers
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST, 1)
    s.bind((IP, PORT))
    my_packet = [IP, name]

    s.sendto(bytes(','.join(my_packet), 'utf-8'), (str(net.broadcast_address), PORT))

    #print(peers)

    print('sent from', socket.getnameinfo(socket.getaddrinfo(IP, PORT)[0][4], socket.NI_DGRAM))

    #s.settimeout(10.0)
    addr_received_previous = ''   #### and (newaddr != addr_received_previous)
    while True:
        newdata, newaddr = s.recvfrom(BUFFER)

        if(newdata) and not(IP == newaddr[0]) and ((newdata.decode('utf-8').split(',')[0]) not in [peer[0] for peer in peers]):
        #    print('as' + (newdata.decode('utf-8').split(',')[0]) + '1asdas')
        #    print('awsd')
            peer = newdata.decode('utf-8').split(',')
            peers.append(peer)
            #print(peers)
            print(datetime.now().strftime('%H:%M') + ' ' + peer[1] + '(' + peer[0] + ') connected')
            s.sendto(bytes(','.join(my_packet), 'utf-8'), (str(net.broadcast_address), PORT))
            addr_received_previous = newaddr
            update_peers()


def update_peers():
    global peers
    need_history = True
    for peer in peers:
        if(len(peer) == 2):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
            peer.append(s)
            s.bind((IP, 0))
            try:
                s.connect((peer[0], PORT))

                if(need_history) and not(peers == []):
                    try:
                        message_history = s.recv(BUFFER)
                        for message in message_history.decode('utf-8').split(';'):
                            print(message)
                        need_history = False
                    except (ConnectionResetError):
                        continue
            except TimeoutError:
                continue
    #print(peers)


def connect_to_new(name):
    global peers
    global messages

    while(True):
    #    print(peers, 'tut')
        print('Enter your message:')
        req = input()
        if(req != 'quit()'):
            print(datetime.now().strftime('%H:%M') + ' ' + name + '(' + IP + '): ' + req)
            req = name + '(' + IP + '): ' +  req
            messages.append(datetime.now().strftime('%H:%M') + ' ' + req)
            for peer in peers:
                try:
                    peer[2].send(bytes(req, 'utf-8'))
                except ConnectionResetError:
                    continue
        else:
            for peer in peers:
                peer[2].shutdown(socket.SHUT_WR)
                peer[2].close()
            os._exit(1)


def chat(name):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
    server.setblocking(0)
    server.bind((IP, PORT))
    server.listen(5)

    inputs = [server]
    outputs = [  ]

    global peers
    global messages

    while(inputs):

        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        for s in readable:
        #    print('1')
            if s is server:
                connection, client_address = s.accept()
                connection.setblocking(0)
                inputs.append(connection)
                #print(messages)
                if(messages):
                    connection.sendall(bytes(';'.join(messages), 'utf-8'))

            else:
                try:
                    data, address = s.recvfrom(BUFFER)
                    if(data):
                        print(datetime.now().strftime('%H:%M') + ' ' +  data.decode('utf-8'))
                        messages.append(datetime.now().strftime('%H:%M') + ' ' +  data.decode('utf-8'))
                        print('Enter your message:')
                    else:
                        client_name = ''
                        for peer in peers:
                            if(peer[0] == client_address[0]):
                                client_name = peer[1]
                        print(datetime.now().strftime('%H:%M') + ' ' + client_name + '(' + client_address[0] + ') disconnected')
                        #print(s)
                        for peer in peers:
                            if(client_address[0] == peer[0]):
                                peer[2].close()
                                peers.remove(peer)
                        inputs.remove(s)
                        s.shutdown(socket.SHUT_WR)
                        s.close()

                        #print(peers)
                        print('Enter your message:')
                except ConnectionResetError:
                    client_name = ''
                    for peer in peers:
                        if(peer[0] == client_address[0]):
                            client_name = peer[1]
                    print(datetime.now().strftime('%H:%M') + ' ' + client_name + '(' + client_address[0] + ') disconnected')
                    #print(s)
                    for peer in peers:
                        if(client_address[0] == peer[0]):
                            peer[2].close()
                            peers.remove(peer)
                    inputs.remove(s)
                    s.shutdown(socket.SHUT_WR)
                    s.close()

                    #print(peers)
                    print('Enter your message:')


        for s in writable:
            if s is server:
                print('Enter your message:')
                req = input()
                if(req != 'quit()'):
                    print(datetime.now().strftime('%H:%M') + ' ' + name + '(' + IP + '): ' + req)
                    req = name + '(' + IP + '): ' +  req
                    messages.append(datetime.now().strftime('%H:%M') + ' ' + req)
                    for peer in peers:
                        try:
                            peer[2].send(bytes(req, 'utf-8'))
                        except ConnectionResetError:
                            continue
                else:
                    for peer in peers:
                        peer[2].shutdown(socket.SHUT_WR)
                        peer[2].close()
                    os._exit(1)



if __name__ == '__main__':
    print('After entering chat type quit() to end session \nEnter your name:')
    name = input()
    threading.Thread(target=chat, args=(name,)).start()
    threading.Thread(target=udp_first_connection, args=(name,)).start()
    print(datetime.now().strftime('%H:%M') + ' ' + 'You connected to chat')
    time.sleep(1.0)
    threading.Thread(target=connect_to_new, args=(name,)).start()















def send():
    cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    cs.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST, 1)
#    cs.bind((socket.INADDR_ANY, PORT))

    cs.sendto(b'This is a test', (str(net.broadcast_address), PORT))
    print('sent from', socket.getnameinfo(socket.getaddrinfo(IP, PORT)[0][4], socket.NI_DGRAM))
    cs.close()
        #cs.setblocking(1)

def getshit():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 0))
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #s.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST, 1)
    s.settimeout(10.0)
    while True:
        data, addres = s.recvfrom(BUFFER)

        if(data):
            print(data)

#send()
#getshit()
#threading.Thread(target=getshit(), daemon=True).start()










'''
class socket_udp:
    host = ''
    port = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    def init_socket(self):
        while True:
            print('enter IP : ')
            self.host = str(input())
            if (self.host == '0.0.0.0') or (self.host == 'localhost'):
                break
            else:
                print('host must be localhost or 0.0.0.0')
                continue
        try:
            print('enter PORT : ')
            self.port = int(input())
        except ValueError:
            print('Port must be integer with base 10')
            print('enter PORT : ')
            self.port = int(input())

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind((self.host, self.port))
        print('now listening port ', self.port, ' on IP ', self.host)

    def listen_sock(self):
        while 1:
            try:
                msg, addr = self.sock.recvfrom(256)
                msg = str(msg)[2:len(str(msg)) - 1]
                print(msg, 'from :', addr)
            except KeyboardInterrupt:
                print('input was interrupted by user')
                break
    def send_sock(self):
         while 1:
                print('enter text :')
                text = input()
                text = input()
                self.sock.sendto(text.encode('utf-8'),(self.host, self.port))


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
print(s.getsockname()[0])
s.close()
print(socket.gethostbyname_ex(socket.gethostname())[-1])

sck = socket_udp()

#sck.init_socket()
#threading.Thread(target=sck.listen_sock, daemon=True).start()
#sck.send_sock()
'''
