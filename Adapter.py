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
    def adapt(self, imap, command):
        com = command.split(' ')
        if com[0] == 'select':
            log = imap.select(com[1])
        elif com[0] == 'close':
            log = imap.close_mailbox()
        elif com[0] == 'status':
            log = imap.get_status_mailbox(com[1], com[2:])
        elif com[0] == 'delete':
            log = imap.delete_check_mails()
        elif com[0] == 'search':
            log = imap.search_mail(com[1:])
        elif com[0] == 'flag':
            if com[1] == 'del':
                log = imap.del_flag_mail(com[2], com[3:])
            elif com[1] == 'add':
                log = imap.add_flag_mail(com[2], com[3:])
            elif com[1] == 'change':
                log = imap.change_flag_mail(com[2], com[3:])
        elif com[0] == 'fetch':
            log = imap.fetch(com[1], com[2:])
        elif com[0] == 'date':
            log, data = imap.get_date(com[1])
        elif com[0] == 'text':
            log = imap.get_text(com[1])
        elif com[0] == 'subject':
            log = imap.get_subject(com[1])
        elif com[0] == 'message':
            log = imap.get_message(com[1])
        elif com[0] == 'logout':
            log = imap.logout()
        elif com[0] == 'help':
            log = print_help()
        else:
            log = 'Неверная команда, напишите help, для получения справки'

        return log
