import sqlite3
import string
import random
import hashlib
import os.path

print("*" * 80)
print("\t\t\t       PASSWORD VAULT")
print("This service creates secure passwords for your accounts and remembers them!")
print("\t\t\tPress q to quit at ant time")
print("*" * 80)
print()


def encoder(text):
    return str(hashlib.sha256(text.encode('utf-8')).hexdigest())


BANK = string.ascii_letters + string.digits + string.punctuation

if os.path.exists('stored.txt'):
    pass
else:
    password = input("What would you like your MASTER PASSWORD to be? : ")
    initial_encoded = encoder(password)

    with open('stored.txt', 'a') as file:
        file.write(initial_encoded)

key = input("MASTER PASSWORD: ")
in_file = open('stored.txt', 'r')
master_password = in_file.read()

while master_password != encoder(key):
    if key == 'q':
        print("Goodbye!")
        break
    key = input("MASTER PASSWORD: ")

connection = sqlite3.connect("passwords.db")
cursor = connection.cursor()


def command_prompts():
    print('*' * 40)
    print('Command Prompts:')
    print('\tq - to quit')
    print('\tgp - get password')
    print('\tap - add new password')
    print('\tdp - delete a password')
    print('*' * 40)


def create_password():
    required = [random.choice(string.ascii_uppercase), random.choice(string.ascii_lowercase),
                random.choice(string.digits), random.choice(string.punctuation)]
    random.shuffle(required)
    generated_password = []

    for x in required:
        generated_password.append(x)

    for i in range(random.randrange(10, 16) - len(generated_password)):
        generated_password.append(random.choice(BANK))

    random.shuffle(generated_password)
    return ''.join(generated_password)


def get_password(service_):
    cursor.execute("SELECT * FROM passwords WHERE service=:service", {'service': service_})
    password_arr = cursor.fetchall()
    temp = []
    for i in password_arr:
        temp.append(i[1])

    if len(temp) == 0:
        return "No passwords belong to this service!"
    else:
        return '    ,   '.join(temp)


def add_new_password(service_, password):
    with connection:
        cursor.execute("INSERT INTO passwords VALUES (:service, :password)",
                       {'service': service_, 'password': password})


def remove_password(service_):
    with connection:
        cursor.execute("DELETE from passwords WHERE service=:service", {'service': service_})


def main():
    if master_password == encoder(key):
        quit_, get_pass, add_pass, del_pass, yes, no, add_existing, create_new = "q", "gp", "ap", "dp", "Y", "N", "A", "C"
        try:
            cursor.execute("""CREATE TABLE passwords (
                            service text,
                            password text
                            )""")
        except sqlite3.OperationalError:
            print("The database already exists.")

        while True:
            command_prompts()
            user_prompt = input("-> ")

            if user_prompt == quit_.lower():
                print("Goodbye!")
                break
            if user_prompt == get_pass.lower():
                service = input("Name of Service: ")
                print("\n" + service.upper() + " password(s): " + get_password(service))
            if user_prompt == add_pass.lower():
                service = input("Name of NEW service: ")
                option = input("Add existing password or create a password for service? (A/C): ")

                if option == add_existing.upper():
                    password = input("What is the password to " + service + "?: ")
                    add_new_password(service, password)
                    print("\n" + service.upper() + " password created is: " + password)

                if option == create_new:
                    new_password = create_password()
                    add_new_password(service, new_password)
                    print("\n" + service.upper() + " password created is: " + new_password)

            if user_prompt == del_pass.lower():
                cursor.execute('SELECT * FROM passwords')
                all_rows = cursor.fetchall()
                print('1):', all_rows)

                service = input("Enter name of service to be deleted: ")

                verify = input("All passwords associated with this service will be deleted, are you SURE? (Y/N): ")

                if verify.capitalize() == yes.upper():
                    remove_password(service)
                    print("Password has been deleted!")

                    cursor.execute('SELECT * FROM passwords')
                    all_rows1 = cursor.fetchall()
                    print('1):', all_rows1)

                elif verify.capitalize() == no.upper():
                    print('What would you like to do?')

                else:
                    print("Invalid Input! Please try again!")


main()
