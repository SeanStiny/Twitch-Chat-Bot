import socket


class IRC:
    def __init__(self, server, port, log):
        self.sock = socket.socket()
        self.buf = ""
        self.server = server
        self.port = port
        self.log = log

    def connect(self, nickname, password):
        self.sock.connect((self.server, self.port))
        self.__send('PASS oauth:' + password)
        self.__send('NICK ' + nickname)

    def send(self, command, params):
        self.__send(command + ' ' + ' '.join(params))

    def read(self):
        msgstr = ""
        while not msgstr:
            if '\r\n' in self.buf:
                msgstr = self.buf.split('\r\n', 1)[0]
                if self.log:
                    print("< " + msgstr)
                self.buf = self.buf.split('\r\n', 1)[1]
            else:
                rec = self.sock.recv(2048).decode()

                # Check if the socket closed
                if not rec:
                    return None

                # Add socket data to the buffer
                self.buf += rec

        return self.__parse_message(msgstr)

    def __send(self, msg):
        if self.log:
            print("> " + msg)
        self.sock.send((msg + '\n').encode())

    def __parse_message(self, msgstr):
        msg = {
            'tags': None,
            'prefix': None,
            'command': '',
            'params': ''
        }

        msg_split = msgstr.split(' ', 4)
        i = 0

        # Tags
        if msg_split[0][0] == '@':
            tags_split = msg_split[0][1:].split(';')
            tags = {}
            for tag in tags_split:
                tags[tag.split('=')[0]] = tag.split('=')[1]
            msg['tags'] = tags
            i += 1

        # Prefix
        if msg_split[i][0] == ':':
            msg['prefix'] = msg_split[i]
            i += 1

        # Command
        msg['command'] = msg_split[i]

        # Params
        if len(msg_split) > i + 1:
            if len(msg_split) == i + 2:
                msg['params'] = [msg_split[i + 1]]
            else:
                msg['params'] = ' '.join(msg_split[i + 1:])

        return msg
