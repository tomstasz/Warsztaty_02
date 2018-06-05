from clcrypto import check_password
from psycopg2 import connect, OperationalError
from models import User
import argparse


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
        print('dodano uzytkownika')
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
    else:
        print('błąd zmiany hasła')
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


def update_user(email, data):
    cnx = connection()
    cursor = cnx.cursor()
    updated = display_one_user(email)

    if "@" in data:
        updated.email = data
        print("zmiana maila")
    else:
        updated.username = data
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
        print(user.username + '\n' + user.email + '\n')
    cursor.close()
    cnx.close()
    return user_list


parser = argparse.ArgumentParser('Zarządzaj swoim kontem użytkownika')
user_operations = parser.add_argument_group()
user_operations.add_argument('-u', '--username', type=str,
                             help='twój login')

user_operations.add_argument('-m', '--mail', type=str,
                             help='twój email')

user_operations.add_argument('-p', '--password', type=str,
                             help='twoje hasło (min. 8 znaków)')

user_operations.add_argument('-n', '--new_pass', type=str,
                             help='nowe hasło (min. 8 znaków)')

user_operations.add_argument('-l', '--list', action='store_true',
                             help='wyświetl wszystkich użytkowników')

user_operations.add_argument('-d', '--delete', action='store_true',
                             help='usunięcie użytkownika')

user_operations.add_argument('-e', '--edit', type=str,
                             help='zmiana loginu/maila (podaj nowy login lub mail)')

args = parser.parse_args()

if (args.username and args.mail and args.password) \
        and not (args.edit or args.delete or args.new_pass):
    create_user(args.username, args.mail, args.password)
elif args.list:
    print("Lista uzytkowników:\n")
    users = display_all_users()
elif (args.username and args.mail and args.password) and args.delete:
    delete_user(args.mail, args.password)
elif (args.username and args.mail and args.password) and args.edit:
    update_user(args.mail, args.edit)
elif (args.username and args.mail and args.password) and args.new_pass:
    change_user_password(args.mail, args.password, args.new_pass)
else:
    print('wpisz -h, aby uzyskać pomoc i zobaczyć możliwe opcje')




# create_user('tom_01', 'tom_01@onet.pl', 'abrakadabra')
# create_user('barbara007', 'barbara.k@interia.pl', 'superduper18')
# create_user('Adam Kowal', 'adam.kowal@o2.pl', 'moje_haslo')
# create_user('SuperAnna', 'annK@o2.pl', 'hokus-pokus')
# 'Antoni Banderas', antoniBan@onet.pl, czary-mary

