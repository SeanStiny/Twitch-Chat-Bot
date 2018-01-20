import IRC
import Database


class Bot:
    def __init__(self, channel):
        self.channel = channel
        self.irc = None
        self.botname = None
        self.database = Database.Database("database.db")
        self.commands = None

    def start(self, log):
        if not self.database.exists():
            self.database.set_up()
            botname = input("Enter your bot's Twitch username: ")
            oauth = input("Enter your bot's Twitch oauth token: ")
            self.database.store_login(botname, oauth)

        data = self.database.get_data()
        print(data)
        self.botname = data['login'][0]
        oauth = data['login'][1]
        self.commands = data['commands']

        print("Connecting to Twitch Chat IRC...")
        self.irc = IRC.IRC('irc.chat.twitch.tv', 6667, log)
        self.irc.connect(self.botname, oauth)

        connected = True
        while connected:
            connected = self.__poll_events()

    def __poll_events(self):
        event = self.irc.read()

        if event is None:
            return False

        # Ping
        if event['command'] == 'PING':
            self.irc.send('PONG', [event['params'][0]])

        # Welcome message
        elif event['command'] == '001':
            # Request twitch-specific IRC features
            self.irc.send('CAP REQ', [':twitch.tv/membership'])
            self.irc.send('CAP REQ', [':twitch.tv/tags'])
            self.irc.send('CAP REQ', [':twitch.tv/commands'])

            # Join the IRC channel
            print(f"Joining channel '{self.channel}'...")
            self.irc.send('JOIN', ['#' + self.channel.lower()])

        # Joined room
        elif event['command'] == 'JOIN':
            if event['prefix'][1:len(self.botname)+1] == self.botname.lower():
                print("Joined channel '" + event['params'][0][1:] + "'")

        # Chat message
        elif event['command'] == 'PRIVMSG':
            sender = event['prefix'][1:].split('!', 1)[0]
            mod = event['tags']['mod'] == '1' or sender == self.channel
            msg = event['params'].split(' ', 1)[1][1:]

            # Handle chat commands
            if msg[0] == '!':
                msg_split = msg[1:].split(' ', 1)
                command = msg_split[0]
                if len(msg_split) == 2:
                    params = msg_split[1]
                else:
                    params = ""
                self.__chat_command(command.lower(), params, mod, sender)

        return True

    def __send_chat(self, msg):
        self.irc.send('PRIVMSG', [f'#{self.channel.lower()}', f':{msg}'])

    def __chat_command(self, prompt, params, mod, sender):
        # Add command
        if (prompt == 'add' or prompt == 'addmod') and mod:
            if mod:
                params_split = params.split(' ', 1)
                if len(params_split) < 2:
                    self.__send_err_params(prompt, sender)
                else:
                    added_prompt = params_split[0]
                    added_response = params_split[1]

                    modonly = False
                    if prompt == 'addmod':
                        modonly = True

                    self.commands[added_prompt] = (added_response, modonly)
                    self.database.add_command(added_prompt, added_response, modonly)
                    self.__send_chat(f"Added a new command: !{added_prompt}")
            else:
                self.__send_err_mod(prompt, sender)

        # Remove command
        elif prompt == 'remove' and mod:
            if self.commands.pop(params, False):
                self.database.delete_command(params)
                self.__send_chat(f"Command has been removed: !{params}")
            else:
                self.__send_err_command(params, sender)

        # Custom commands
        elif prompt in self.commands:
            modonly = self.commands[prompt][1]
            if modonly and not mod:
                self.__send_err_mod(prompt, sender)
            else:
                response = self.commands[prompt][0]
                if params:
                    response = response.replace("[]", params)
                self.__send_chat(response)

        else:
            self.__send_err_command(prompt, sender)

    def __send_err_params(self, prompt, sender):
        self.__send_chat(f"@{sender} You did not provide enough parameters for command: !{prompt}")

    def __send_err_command(self, prompt, sender):
        self.__send_chat(f"@{sender} Unknown command: !{prompt}")

    def __send_err_mod(self, prompt, sender):
        self.__send_chat(f"@{sender} You need mod privileges to use command: !{prompt}")
