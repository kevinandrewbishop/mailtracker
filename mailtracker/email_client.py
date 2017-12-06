import imaplib
import re


class EmailClient():
    def __init__(self, email, password, host = None, port = 993, folder = 'INBOX'):
        '''

        Parameters
        ==========
        email: str, email addres. E.g. 'foo@example.com'
        password: str, password for email address. It is preferable to store
            this as an environment variable or input using getpass rather than
            as plaintext
        host: str, default None. The imap ssl host. E.g. 'imap.mail.yahoo.com'
            If none, it will try to deduce host from email address.
        port: int, default 993. Port that host is listening on.
        Folder: str, default INBOX. The folder where the email is stored.
            e.g. "sent", "inbox", "visa"
        '''
        self._email = email
        self._password = password
        self._port = port
        self._host = host
        if host is None:
            self._host, self._port = self._get_host(email)
        self.folder = folder
        self._create_server()

    def _create_server(self):
        '''
        Creates an imaplib server object and connects to the email server.
        '''
        self.server = imaplib.IMAP4_SSL(self._host, self._port)
        self.server.login(self._email, self._password)
        _, num_messages = self.select(self.folder)
        self.num_messages = int(num_messages[0])

    def _logout(self):
        '''
        Disconnects from the email server.
        '''
        self.server.logout()

    def reconnect(self):
        '''
        Reconnects to the email server. Often the connection
        is lost after a few minutes.
        '''
        self._logout()
        self._create_server()

    def select(self, folder):
        '''
        Sets the email working folder (e.g. inbox, sent, etc.)
        '''
        return self.server.select(folder)

    def _get_host(self, email):
        '''
        Extracts imap host and port number based on the email address. If the
        domain of the email is not recognized, it will try 'imap.domain.com'
        which is fairly standard.

        Parameters
        ==========
        email: str, the email address. E.g. 'foo@example.com'

        Notes
        =====
        Please note that Gmail by default does not allow users to access
        their email in this way. You can change this setting here:
        https://support.google.com/mail/accounts/answer/78754
        '''
        #extract domain, e.g. 'yahoo.com'
        domain = email.split('@')[1]
        #Dict of known host/port tuples
        imap = {
            'yahoo.com': ('imap.mail.yahoo.com', 993),
            'gmail.com': ('imap.gmail.com', 993)
            }
        if imap.get(domain):
            return imap.get(domain)
        else:
            msg = 'Domain "%s" not recognized. Trying "imap.%s"'
            raise Warning(msg %(domain, domain))
            return ('imap.%s' %domain, 993)

    def _fetch(self, message_set, message_parts = '(BODY[TEXT])'):
        '''
        Fetches the message.
        '''
        return self.server.fetch(message_set, message_parts)

    def read_message(self, message_set = None, regex = None):
        '''
        Read a message and apply regular expression to extract desired text.

        If message_set is None, retrieves the latest message.
        If regex is None, returns the entire message.
        '''
        if message_set is None:
            message_set = str(self.num_messages)
        stat, msg = self._fetch(message_set)
        if stat == 'OK':
            if regex is not None:
                msg = msg[0][1].decode('utf-8')
                return re.findall(regex, msg)
            else:
                return msg[0][1]
        raise Warning("Message id %s failed to retrieve message" %message_set)
        return None
