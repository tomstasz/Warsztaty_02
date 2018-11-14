from clcrypto import check_password
from psycopg2 import connect, OperationalError
from models import User, Message
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
        print('dodano użytkownika')
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


def create_message(from_id, to_id, tekst):
    cnx = connection()
    cursor = cnx.cursor()
    new_message = Message()
    new_message.from_id = from_id
    new_message.to_id = to_id
    new_message.tekst = tekst
    new_message.save_to_db(cursor)
    cnx.commit()
    print('dodano komunikat')
    cursor.close()
    cnx.close()


def check_messages(email):
    cnx = connection()
    cursor = cnx.cursor()
    messages_received = Message.get_all_messages_for_user(cursor, email)
    if messages_received:
        return messages_received
    cursor.close()
    cnx.close()


def delete_message(id):
    cnx = connection()
    cursor = cnx.cursor()
    message = Message.get_message_by_id(cursor, id)
    if message:
        message.delete(cursor)
        cnx.commit()
        print("wiadomość usunięta")
    else:
        print("błąd usuwania")
    cursor.close()
    cnx.close()


def check_id(email):
    cnx = connection()
    cursor = cnx.cursor()
    res = Message.get_id(cursor, email)
    cursor.close()
    cnx.close()
    return int(res)


def show_all_messages():
    cnx = connection()
    cursor = cnx.cursor()
    all_messages = Message.get_all_messages(cursor)
    for message in all_messages:
        print("{} \n {} \n {} \n\n".format(message.id, message.creation_date, message.tekst))
    cursor.close()
    cnx.close()
    return all_messages


parser = argparse.ArgumentParser('Zarządzaj kontem użytkownika i wysyłaniem komunikatów')

parser.add_argument('-u', '--username', type=str, help='twój login')

parser.add_argument('-m', '--mail', type=str, help='twój email')

parser.add_argument('-p', '--password', type=str, help='twoje hasło (min. 8 znaków)')


parser.add_argument('-n', '--new_pass', type=str, help='nowe hasło (min. 8 znaków)')

parser.add_argument('-l', '--list', action='store_true',
                    help='wyświetl wszystkich użytkowników lub komunikaty')

parser.add_argument('-d', '--delete', action='store_true', help='usunięcie użytkownika')

parser.add_argument('-e', '--edit', type=str, help='zmiana loginu/maila (podaj nowy login lub mail)')

parser.add_argument('-t', '--to', type=str, help='mail odbiorcy')

parser.add_argument('-s', '--send', type=str, help='wysyłany komunikat')


args = parser.parse_args()

if (args.username and args.mail and args.password) \
        and not (args.edit or args.delete or args.new_pass):
    create_user(args.username, args.mail, args.password)
elif args.list and not (args.mail or args.password or args.edit or args.new_pass):
    print("Lista uzytkowników:\n")
    users = display_all_users()
elif (args.username and args.mail and args.password) and args.delete:
    delete_user(args.mail, args.password)
elif (args.username and args.mail and args.password) and args.edit:
    update_user(args.mail, args.edit)
elif (args.username and args.mail and args.password) and args.new_pass:
    change_user_password(args.mail, args.password, args.new_pass)
elif args.mail and args.password and args.list:
    user = display_one_user(args.mail)
    if user and check_password(args.password, user.hashed_password):
        check_messages(args.mail)
    else:
        print("błędny login lub hasło")
elif args.mail and args.password and not (args.to and args.send):
    raise Exception("proszę podać mail adresata i treść wiadomości")
elif args.mail and args.password and args.to and args.send:
    user = display_one_user(args.mail)
    user_to = display_one_user(args.to)
    if user and check_password(args.password, user.hashed_password):
        if user_to:
            create_message(check_id(args.mail), check_id(args.to), args.send)
        else:
            raise Exception("nie znaleziono adresata")
    else:
        print("błędny login lub hasło")
else:
    print('wpisz -h, aby uzyskać pomoc i zobaczyć możliwe opcje\n')





