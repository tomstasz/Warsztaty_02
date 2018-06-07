from clcrypto import password_hash
from datetime import datetime


class User:
    __id = -1
    username = None
    __hashed_password = None
    email = None

    def __init__(self):
        self.__id = -1
        self.username = ""
        self.email = ""
        self.__hashed_password = ""

    @staticmethod
    def get_user_by_email(cursor, email):
        sql = """SELECT id, username, email, hashed_password  FROM users 
                 WHERE email=%s"""
        cursor.execute(sql, (email,))
        data = cursor.fetchone()
        if data:
            loaded_user = User()
            loaded_user.__id = data[0]
            loaded_user.username = data[1]
            loaded_user.email = data[2]
            loaded_user.__hashed_password = data[3]
            return loaded_user

    def save_to_db(self, cursor):
        if self.__id == -1:
            sql ="""INSERT INTO users(username, email, hashed_password) 
                    VALUES(%s, %s, %s) RETURNING id"""
            cursor.execute(sql, (self.username, self.email, self.hashed_password))
            #(id,) = cursor.fetchone()
            self.__id = cursor.fetchone()[0]
            return True
        else:
            sql = """UPDATE users SET username=%s, email=%s, hashed_password=%s 
                     WHERE id=%s"""
            values = (self.username, self.email, self.hashed_password, self.__id)
            cursor.execute(sql, values)
            return True

    def delete(self, cursor):
        if self.__id == -1:
            print("Obiekt nie jest zapisany w bazie")
        else:
            sql = """DELETE FROM users WHERE email=%s"""
            cursor.execute(sql, (self.email,))
            self.__id = -1
            return True
            # raise NotImplementedError

    @property
    def hashed_password(self):
        return self.__hashed_password

    def set_password(self, new_password):
        self.__hashed_password = password_hash(new_password)

    @staticmethod
    def get_all_users(cursor):
        sql = """SELECT id, username, email, hashed_password FROM users"""
        res = []
        cursor.execute(sql)
        for row in cursor.fetchall():
            loaded_user = User()
            loaded_user.__id = row[0]
            loaded_user.username = row[1]
            loaded_user.email = row[2]
            loaded_user.__hashed_password = row[3]
            res.append(loaded_user)
        return res


class Message:
    __id = -1
    from_id = None
    to_id = None
    tekst = None

    def __init__(self):
        self.__id = -1
        self.from_id = ""
        self.to_id = ""
        self.tekst = ""
        self.creation_date = datetime.now().strftime('%d-%m-%Y %H:%M')

    @property
    def id(self):
        return self.__id

    @staticmethod
    def get_message_by_id(cursor, id):
        sql = """SELECT id, from_id, to_id, tekst, creation_date  FROM messages 
                     WHERE id=%s"""
        cursor.execute(sql, (id,))
        data = cursor.fetchone()
        if data:
            loaded_message = Message()
            loaded_message.__id = data[0]
            loaded_message.from_id = data[1]
            loaded_message.to_id = data[2]
            loaded_message.tekst = data[3]
            loaded_message.creation_date = data[4]
            return loaded_message

    def save_to_db(self, cursor):
        if self.__id == -1:
            sql ="""INSERT INTO messages(from_id, to_id, tekst, creation_date) 
                    VALUES(%s, %s, %s, %s) RETURNING id"""
            values = (self.from_id, self.to_id, self.tekst, self.creation_date)
            cursor.execute(sql, values)
            self.__id = cursor.fetchone()[0]
            return True
        else:
            print('message already exists')

    @staticmethod
    def get_all_messages(cursor):
        sql = """SELECT id, from_id, to_id, tekst, creation_date  FROM messages"""
        res = []
        cursor.execute(sql)
        for data in cursor.fetchall():
            loaded_message = Message()
            loaded_message.__id = data[0]
            loaded_message.from_id = data[1]
            loaded_message.to_id = data[2]
            loaded_message.tekst = data[3]
            loaded_message.creation_date = data[4]
            res.append(loaded_message)
        return res

    @staticmethod
    def get_all_messages_for_user(cursor, email):
        sql = """SELECT messages.tekst,
                        messages.creation_date,
                        sender.username,
                        sender.email
                 FROM messages 
                 JOIN users AS sender ON messages.from_id = sender.id
                 JOIN users AS receiver ON messages.to_id = receiver.id
                 WHERE receiver.email=%s
                 ORDER BY creation_date 
              """
        cursor.execute(sql, (email,))

        for data in cursor.fetchall():
            print(data[2] + '\n' +
                  data[3] + '\n' +
                  str(data[1]) + '\n\n' +
                  data[0] + '\n' + '-------')

    def delete(self, cursor):
        if self.__id == -1:
            print("Obiekt nie jest zapisany w bazie")
        else:
            sql = """DELETE FROM messages WHERE id=%s"""
            cursor.execute(sql, (self.__id,))
            self.__id = -1
            return True

    @staticmethod
    def get_id(cursor, email):
        sql = """SELECT users.id
                     FROM users 
                     WHERE users.email=%s"""

        cursor.execute(sql, (email,))
        user_id = cursor.fetchone()[0]
        if user_id:
            return user_id

