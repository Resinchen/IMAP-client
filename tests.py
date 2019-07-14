import socket
import ssl
import unittest

from IMAP import ImapSSL


class TestIMAPClient(unittest.TestCase):
    def test_connect(self):
        sock = ssl.SSLSocket(socket.socket())
        sock.connect(('imap.yandex.ru', 993))
        self.assertTrue(b'OK' in sock.recv(1024))

    def test_login(self):
        imap = ImapSSL('yandex')
        imap.login('testIMAPChe@yandex.ru', 'fortest')
        self.assertTrue(b'OK' in sock.recv(1024))


if __name__ == '__main__':
    unittest.main()
