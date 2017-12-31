import imaplib
import email
import re


class EmailClient():
    def __init__(self, email, password, host = None, port = 993,
        folder = 'INBOX', metadata = None):
        '''
        EmailClient can fetch email and return it as a python dictionary. By
        default it reads the body of the most recent email in the inbox.
        It can fetch metadata such as Date, To, From, and Subject. It can also
        extract elements from the body of the email using regular expressions.
        Each piece of metadata as well as the text itself is stored as key-value
        pairs in the dictionary.

        Example
        =======
        >>> address = 'foo@example.com'
        >>> password = 'monkey'
        >>> folder = 'my_folder'
        >>> metadata = ['Date', 'Subject']
        >>> client = EmailClient(address, password, folder, metadata)
        >>> regex = 'some [fake] regex*'
        >>> client.read_message(regex)
        >>> {'Date': '30 Dec 2017 20:38:48 -0500', 'Subject': 'Deal at Kroger!',
            'text': [['chicken', '$10.99', 'coupon']]}

        Parameters
        ==========
        email: str, email addres. E.g. 'foo@example.com'
        password: str, password for email address. It is preferable to store
            this as an environment variable or input using getpass rather than
            as plaintext
        host: str, default None. The imap ssl host. E.g. 'imap.mail.yahoo.com'
            If none, it will try to deduce host from email address.
        port: int, default 993. Port that host is listening on.
        folder: str, default INBOX. The folder where the email is stored.
            e.g. "sent", "inbox", "visa"
        metadata: str, list of str, or None. Default None. Any metadata about
            the email to capture. Examples: ['To', 'From', 'Date', 'Subject']
            Any keys that an email Message object might have.
        '''
        self._email = email
        self._password = password
        self._port = port
        self._host = host
        if host is None:
            self._host, self._port = self._get_host(email)
        self.folder = folder
        self._metadata = self._prep_metadata(metadata)
        self._create_server()

    def _prep_metadata(self, metadata):
        if metadata is None:
            return None
        elif isinstance(metadata, list):
            return metadata
        elif isinstance(metadata, str):
            return [metadata]
        else:
            msg = 'metadata must be str, list, or None, got %s'
            raise TypeError(msg %type(metadata))

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
        out = dict()
        if message_set is None:
            message_set = str(self.num_messages)
        #Gather metadata from email if user requested it
        if self._metadata is not None:
            stat, msg = self._fetch(message_set, '(RFC822)')
            msg = msg[0][1]
            message = email.message_from_bytes(msg)
            #If list of metadata,
            for k in self._metadata:
                out[k] = message[k]
        stat, msg = self._fetch(message_set)
        if stat == 'OK':
            if regex is not None:
                msg = msg[0][1].decode('utf-8')
                text = re.findall(regex, msg)
            else:
                text = msg[0][1]
            out['text'] = text
            return out
        raise Warning("Message id %s failed to retrieve message" %message_set)
        return None
