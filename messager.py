from clcrypto import check_password
from psycopg2 import connect, OperationalError
from models import User


def connection():
    user = 'postgres'
    password = 'coderslab'
    host = 'localhost'
    database = 'warsztaty02'
    try:
        conn = connect(user=user,
                       password=password,
                       host=host,
                       database=database)
        return conn
    except OperationalError:
        return None


def create_user(username, email, password):
    cnx = connection()
    cursor = cnx.cursor()
    data = User.get_user_by_email(cursor, email)
    if data:
        cursor.close()
        cnx.close()
        raise Exception("user exist")
    else:
        new_user = User()
        new_user.username = username
        new_user.email = email
        new_user.set_password(password)
        new_user.save_to_db(cursor)
        cnx.commit()
        cursor.close()
        cnx.close()


def change_user_password(email, password, new_password):
    cnx = connection()
    cursor = cnx.cursor()
    user = User.get_user_by_email(cursor, email)
    if user and check_password(password, user.hashed_password) and len(new_password) > 8:
        user.set_password(new_password)
        user.save_to_db(cursor)
        cnx.commit()
        print('hasło zmienione')
    cursor.close()
    cnx.close()


def delete_user(email, password):
    cnx = connection()
    cursor = cnx.cursor()
    user = User.get_user_by_email(cursor, email)
    if user and check_password(password, user.hashed_password):
        user.delete(cursor)
        cnx.commit()
        print("użytkownik usunięty")
    else:
        print("błąd usuwania")
    cursor.close()
    cnx.close()


def display_one_user(email):
    cnx = connection()
    cursor = cnx.cursor()
    user = User.get_user_by_email(cursor, email)
    print("""{}\n{}""".format(user.username, user.email))
    cursor.close()
    cnx.close()
    return user


def update_user(email, *args):
    cnx = connection()
    cursor = cnx.cursor()
    updated = display_one_user(email)
    if len(args) > 1:
        updated.username = args[0]
        updated.email = args[1]
        print("zmiana nazwy użytkownika i maila")
    else:
        if "@" in args[0]:
            updated.email = args
            print("zmiana maila")
        else:
            updated.username = args
            print("zmiana nazwy użytkownika")

    updated.save_to_db(cursor)
    cnx.commit()
    cursor.close()
    cnx.close()


def display_all_users():
    cnx = connection()
    cursor = cnx.cursor()
    user_list = User.get_all_users(cursor)
    for user in user_list:
        print(user.username, user.email)
    cursor.close()
    cnx.close()
    return user_list





# create_user('tom_01', 'tom_01@onet.pl', 'abrakadabra')
# create_user('barbara007', 'barbara.k@interia.pl', 'superduper18')
# create_user('Adam Kowal', 'adam.kowal@o2.pl', 'moje_haslo')
# create_user('SuperAnna', 'annK@o2.pl', 'hokus-pokus')


