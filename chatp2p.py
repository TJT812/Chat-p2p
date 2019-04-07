import socket
import time
import ipaddress
import subprocess
import threading

PORT = 0

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

def send():
    cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    cs.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST, 1)
    #cs.bind((IP, PORT))

    cs.sendto(b'This is a test', (str(net.broadcast_address), PORT))
    print('sent from', socket.getnameinfo(socket.getaddrinfo(IP, PORT)[0][4], socket.NI_DGRAM))
    cs.close()
        #cs.setblocking(1)

def getshit():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST, 1)
    s.bind((IP, PORT))
    print('yo')
    while True:
        try:
            data, addres = s.recvfrom(2048)

            print(addres)
    #if(addres == net.broadcast_address):
            print('done received:', data)
        except KeyboardInterrupt:
            print('input was interrupted by user')
            break

send()
threading.Thread(target=getshit()).start()

















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
