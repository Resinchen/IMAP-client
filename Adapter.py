from IMAP import ImapSSL


def print_help():
    help = 'login *email* *password* - авторизация\n' \
           '\n' \
           'select *mailbox* - выбор ящика\n' \
           'close - закрыть ящик\n' \
           'status *mailbox* *args* статус ящика\n' \
           '\n' \
           'delete mail - удалить помеченные сообщения\n' \
           'search *args* - поиск сообщений\n' \
           '\n' \
           'flag del *num* - удалить флаг\n' \
           'flag add *num* - добавить флаг\n' \
           'flag change *num* - изменить флаг\n' \
           '\n' \
           'fetch *num* *arg* - получить конкретную информацию\n' \
           'data *num* - получить дату сообщения\n' \
           'text *num* - получить текст сообщения\n' \
           'subject *num* - получить тему сообшения\n' \
           'message *num* - получить все сообщение\n' \
           '\n' \
           'logout - выход из аккаунта\n' \
           '\n' \
           'exit - выход\n'


class Adapter:
    def adapt(self, imap: type(ImapSSL), command: str):
        commands = {
            'select': lambda com: imap.select(com[1]),
            'close': lambda com: imap.close_mailbox(),
            'status': lambda com: imap.get_status_mailbox(com[1], com[2:]),
            'delete': lambda com: imap.delete_check_mails(),
            'search': lambda com: imap.search_mail(com[1:]),
            'flag': lambda com: flag_operations[com[1]](com),
            'fetch': lambda com: imap.fetch(com[1], com[2:]),
            'date': lambda com: imap.get_date(com[1]),
            'text': lambda com: imap.get_text(com[1]),
            'subject': lambda com: imap.get_subject(com[1]),
            'message': lambda com: imap.get_message(com[1]),
            'logout': lambda com: imap.logout(),
            'help': lambda com: print_help(),
        }

        flag_operations = {
            'del': lambda com: imap.del_flag_mail(com[2], com[3:]),
            'add': lambda com: imap.add_flag_mail(com[2], com[3:]),
            'change': lambda com: imap.change_flag_mail(com[2], com[3:])
        }

        com = command.split(' ')
        
        try:
            log = commands[com[0]](com)
        except KeyError:
            log = 'Неверная команда, напишите help, для получения справки'

        return log
