from Adapter import Adapter
from IMAP import ImapSSL, State


class Client:
    def __init__(self):
        self.imap = None

    def start(self):
        self.hello()
        self.logined()
        adapter = Adapter()
        self.work(adapter)

    def hello(self):
        print('Привет!')
        print('Куда будем подключаться?')
        print()
        service = input()
        print()
        self.imap = ImapSSL(service)

    def logined(self):
        while self.imap.state == 'LOGIN':
            print('Введите email')
            email = input()
            print()
            print('Введите пароль')
            password = input()
            print()
            print('Подключение...')
            print('Ожидайте...')
            login = self.imap.login(email, password)
            if login.find(b'OK') != -1:
                print('Подключено, пожалуйста продолжайте...')
                self.imap.state = State.SELECT.value
            else:
                print()
                print('Неверные данные. Попробуйте еще раз')
                print()
        print()
        print('Logined')
        print('---------------------')

    def work(self, adapter: type(Adapter)):
        while self.imap.state != 'EXIT':
            while self.imap.state == 'SELECT':
                self.selected()
            while self.imap.state == 'WORK':
                self.command_handler(adapter)
        print('Exited')

    def selected(self):
        print('Выберите ящик')
        print()
        mailbox = input()
        print()
        select = self.imap.select(mailbox)
        if select.find(b'OK') != -1:
            self.imap.state = State.WORK.value
        else:
            print('Неверные данные. Проверьте правильность')
            print()
        print('Selected')
        print('---------------------')

    def command_handler(self, adapter: type(Adapter)):
        print('Что будем делать?)')
        print()
        command = input()

        if command == 'exit':
            self.imap.state = State.EXIT.value
        else:
            log = adapter.adapt(self.imap, command)

            if log.find(b'OK CLOSE') != -1:
                self.imap.state = State.SELECT.value
            if log.find(b'OK LOGOUT') != -1:
                self.imap.state = State.EXIT.value
            print(log.decode())
        print('++++++++++++++++++')
        print()
