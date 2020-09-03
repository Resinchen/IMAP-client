import base64
import itertools
import quopri
import socket
import ssl
import time
from typing import List
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
    def __init__(self, service: str):
        self.__iterator = itertools.count(start=0, step=1)
        self.next_id = lambda : next(self.__iterator)
        self.id = 0
        self.state = State.LOGIN.value
        self.sock = ssl.wrap_socket(socket.socket())
        self.sock.connect(self._set_addr(service))
        self.sock.recv(1024)


    def _set_addr(self, service: str):
        _imap_addr = {'yandex': 'imap.yandex.ru', 'mail.ru': 'imap.mail.ru', 'google': 'imap.gmail.com'}
        return _imap_addr.get(service.lower()), 993

    def _read_all(self, num_sendess: int):
        data = b''
        exit_str = f'A{num_sendess} '
        while data.find(exit_str.encode()) == -1:
            d = self.sock.recv(1024)
            data += d
        return data

    def login(self, email: str, password: str):
        self.id = self.next_id()
        self.sock.send(f'A{self.id} LOGIN {email} {password}\r\n'.encode())
        time.sleep(10)
        log = self._read_all(self.id)
        return log

    def select(self, mailbox='INBOX'):
        self.id = select.next_id()
        self.sock.send(f'A{self.id} SELECT {mailbox}\r\n'.encode())
        log = self._read_all(self.id)
        return log

    def close_mailbox(self):
        self.id = select.next_id()
        self.sock.send(f'A{self.id} CLOSE\r\n'.encode())
        log = self._read_all(self.id)
        return log

    def delete_check_mails(self):
        self.id = select.next_id()
        self.sock.send(f'A{self.id} EXPUNGE\r\n'.encode())
        log = self._read_all(self.id)
        return log

    def search_mail(self, arguments: List[str]):
        self.id = select.next_id()
        search_flag = ' '.join(arguments)
        self.sock.send(f'A{self.id} SEARCH {search_flag}\r\n'.encode())
        log = self._read_all(self.id)
        return log

    def _store_flags(self, num: str, operation_flag: str, flags: List[str]):
        self.id = select.next_id()
        flag = '\\' + ' \\'.join(flags)
        self.sock.send(f'A{self.id} STORE {num} {operation_flag}FLAGS ({flag})\r\n'.encode())

    def del_flag_mail(self, num: str, flags: str):
        self._store_flags(num, '-', flags)
        log = self._read_all(self.id)
        return log

    def add_flag_mail(self, num: str, flags: str):
        self._store_flags(num, '+', flags)
        log = self._read_all(self.id)
        return log

    def change_flag_mail(self, num: str, flags: str):
        self._store_flags(num, '', flags)
        log = self._read_all(self.id)
        return log

    def get_status_mailbox(self, mailbox: str, arguments: List[str]):
        self.id = select.next_id()
        status_flag = ' '.join(arguments)
        self.sock.send(f'A{self.id} STATUS {mailbox} ({status_flag})\r\n'.encode())
        log = self._read_all(self.id)
        return log

    def fetch(self, num: str, argument: str):
        self.id = select.next_id()
        self.sock.send(f'A{self.id} FETCH {num} {argument}\r\n'.encode())

    def get_date(self, num: str):
        self.fetch(num, 'BODY[HEADER.FIELDS (DATE)]')
        log = self._read_all(self.id)
        return log

    def get_text(self, num: str):
        charset, codec = self._get_info_for_text(num)
        charset = charset.split('"')[1]

        self.fetch(num, 'BODY[TEXT]')
        text = self._read_all(self.id)
        
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

    def get_message(self, num: str):
        date = self.get_date(num)
        subject = self.get_subject(num)
        text = self.get_text(num)

        msg = f'{num}\n{date.decode()}\n{subject.decode()}\n{text.decode()}'
        return msg.encode()

    def _get_info_for_text(self, num: str):
        self.fetch(num, 'BODY')
        info = self.sock.recv(1024).decode().split(' ')
        codec = info[10]
        charset = info[7]
        return charset, codec

    def logout(self):
        self.id = select.next_id()
        self.sock.send(f'A{self.id} LOGOUT\r\n'.encode())
        log = self._read_all(self.id)
        return log

    def get_subject(self, num: str):
        self.fetch(num, 'BODY[HEADER.FIELDS (SUBJECT)]')
        readed = self._read_all(self.id)
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
