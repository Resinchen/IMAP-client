import base64
import quopri
import socket
import ssl
import time
from enum import Enum


# yandex
# 3 - base64
# 140 - quote
# 4 - 8 bit
# 7 - 7 bit
# 140 - b64 problem

# mail.ru
# 1- b64 problem
# 14 - else

class State(Enum):
    LOGIN = 'LOGIN'
    SELECT = 'SELECT'
    WORK = 'WORK'
    EXIT = 'EXIT'


class ImapSSL:
    def __init__(self, service):
        self.i = 0
        self.state = State.LOGIN.value
        self.sock = ssl.SSLSocket(socket.socket())
        self.sock.connect(self._set_addr(service))
        self.sock.recv(1024)

    def _get_id(self):
        self.i += 1
        return self.i

    def _set_addr(self, services):
        _imap_addr = {'yandex': 'imap.yandex.ru', 'mail.ru': 'imap.mail.ru', 'google': 'imap.gmail.com'}
        addr = _imap_addr.get(services)
        return addr, 993

    def _read_all(self, num_sendess):
        data = b''
        exit_str = 'A{} '.format(num_sendess)
        while data.find(exit_str.encode()) == -1:
            d = self.sock.recv(1024)
            data += d
        return data

    def login(self, email, password):
        self.sock.send('A{} LOGIN {} {}\r\n'.format(self._get_id(), email, password).encode())
        time.sleep(10)
        log = self._read_all(self.i)
        return log

    def select(self, mailbox='INBOX'):
        self.sock.send('A{} SELECT {}\r\n'.format(self._get_id(), mailbox).encode())
        log = self._read_all(self.i)
        return log

    def close_mailbox(self):
        self.sock.send('A{} CLOSE\r\n'.format(self._get_id()).encode())
        log = self._read_all(self.i)
        print(log)
        return log

    def delete_check_mails(self):
        self.sock.send('A{} EXPUNGE\r\n'.format(self._get_id()).encode())
        log = self._read_all(self.i)
        return log

    def search_mail(self, arguments):
        search_flag = ' '.join(arguments)
        self.sock.send('A{} SEARCH {}\r\n'.format(self._get_id(), search_flag).encode())
        log = self._read_all(self.i)
        return log

    def _store_flags(self, num, add_or_del_or_change, flags):
        flag = ' \\'.join(flags)
        self.sock.send('A{} STORE {} {}FLAGS \{}\r\n'.format(self._get_id(), num, add_or_del_or_change, flag).encode())

    def del_flag_mail(self, num, flags):
        self._store_flags(num, '-', flags)
        log = self._read_all(self.i)
        return log

    def add_flag_mail(self, num, flags):
        self._store_flags(num, '+', flags)
        log = self._read_all(self.i)
        return log

    def change_flag_mail(self, num, flags):
        self._store_flags(num, '', flags)
        log = self._read_all(self.i)
        return log

    def get_status_mailbox(self, mailbox, arguments):
        status_flag = ' '.join(arguments)
        self.sock.send('A{} STATUS {} ({})\r\n'.format(self._get_id(), mailbox, status_flag).encode())
        log = self._read_all(self.i)
        print(log)
        return log

    def fetch(self, num, argument):
        self.sock.send('A{} FETCH {} {}\r\n'.format(self._get_id(), num, argument).encode())

    def get_date(self, num):
        self.fetch(num, 'BODY[HEADER.FIELDS (DATE)]')
        log = self._read_all(self.i)
        return log

    def get_text(self, num):
        charset, codec = self._get_info_for_text(num)
        charset = charset.split('"')[1]

        self.fetch(num, 'BODY[TEXT]')
        text = self._read_all(self.i)

        if codec.find('quoted-printable') != -1:
            decode_text = quopri.decodestring(text).decode(charset)
        elif codec.find('base64') != -1:
            pre_text = text[text.find(b'\r\n') + 4:]
            decode_text = base64.decodebytes(pre_text).decode(charset)
        elif codec.find('8bit') != -1:
            decode_text = text.decode(charset)
        elif codec.find('7BIT') != -1:
            decode_text = text.decode(charset)
        elif codec.find('binary') != -1:
            decode_text = text.decode(charset)
        else:
            decode_text = text.decode()
            print('NOTHING')

        return decode_text.encode()

    def get_message(self, num):
        date = self.get_date(num)
        subject = self.get_subject(num)
        text = self.get_text(num)

        msg = '{}\n{}\n{}\n{}'.format(num, date.decode(), subject.decode(), text.decode())
        return msg.encode()

    def _get_info_for_text(self, num):
        self.fetch(num, 'BODY')
        info = self.sock.recv(1024).decode().split(' ')
        codec = info[10]
        charset = info[7]
        return charset, codec

    def logout(self):
        self.sock.send('A{} LOGOUT\r\n'.format(self._get_id()).encode())
        log = self._read_all(self.i)
        return log

    def get_subject(self, num):
        self.fetch(num, 'BODY[HEADER.FIELDS (SUBJECT)]')
        readed = self._read_all(self.i)
        text_s = readed.split(b'?')
        codec = text_s[2]
        charset = text_s[1].decode()
        text = text_s[3]

        if codec == b'Q':
            decode_text = quopri.decodestring(text).decode(charset)
        elif codec == b'B' != -1:
            decode_text = base64.decodebytes(text).decode(charset)
        else:
            decode_text = text.decode()
            print('NOTHING')

        return decode_text.encode()
