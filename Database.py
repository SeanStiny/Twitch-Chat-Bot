import sqlite3
import os


class Database:
    def __init__(self, name):
        self.name = name

    def exists(self):
        return os.path.isfile(self.name)

    def set_up(self):
        conn = sqlite3.connect(self.name)
        c = conn.cursor()
        c.execute("CREATE TABLE login (botname TEXT, oauth TEXT)")
        c.execute("CREATE TABLE commands (prompt TEXT CONSTRAINT prompt_pk PRIMARY KEY, response TEXT, mod INTEGER)")
        conn.commit()
        conn.close()

    def store_login(self, botname, oauth):
        conn = sqlite3.connect(self.name)
        c = conn.cursor()
        c.execute("INSERT INTO login VALUES(?,?)", (botname, oauth))
        conn.commit()
        conn.close()

    def get_data(self):
        conn = sqlite3.connect(self.name)
        c = conn.cursor()

        # Load login data
        c.execute("SELECT * FROM login")
        login = c.fetchone()

        # Load command data
        commands = {}
        for command in c.execute("SELECT * FROM commands"):
            commands[command[0]] = (command[1], command[2])

        conn.close()
        return {'login': login, 'commands': commands}

    def add_command(self, prompt, response, mod):
        conn = sqlite3.connect(self.name)
        c = conn.cursor()
        c.execute("INSERT INTO commands VALUES (?,?,?)", (prompt, response, mod))
        conn.commit()
        conn.close()

    def delete_command(self, prompt):
        conn = sqlite3.connect(self.name)
        c = conn.cursor()
        c.execute("DELETE FROM commands WHERE prompt = ?", (prompt,))
        conn.commit()
        conn.close()
