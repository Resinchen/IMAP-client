import socket
import ssl


def print_data(sock, num):
    data = b''
    exit_str = 'A{}'.format(num)
    while data.find(exit_str.encode()) == -1:
        d = sock.recv(1024)
        data += d
    print(data)


sock = ssl.SSLSocket(socket.socket())
sock.connect(('imap.yandex.ru', 993))
print(sock.recv(1024))
print()
sock.send('A2 LOGIN {} {}\r\n'.format('testIMAPChe@yandex.ru', 'fortest').encode())
print_data(sock, 2)

sock.send('A3 SELECT {}\r\n'.format('INBOX').encode())
print_data(sock, 3)


sock.send('A3 FETCH {} {}\r\n'.format('1', 'ENVELOPE').encode())
data = sock.recv(12000)
print(data)

import email
import email.message

msg = email.message_from_bytes(data, _class=email.message.EmailMessage)

