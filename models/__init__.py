from clcrypto import password_hash, check_password


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


# ustawiamy getter do prywatnej właściwości __hashed password i setter ustawiajacy nowe hasło
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

