import getpass
import bcrypt
import psycopg2

def has_upper(pass1):
    for ch in pass1:
        if ch.isupper():
            return True
    return False

def has_lower(pass1):
    for ch in pass1:
        if ch.islower():
            return True
    return False

def has_symbol(pass1):
    for ch in pass1:
        if not ch.isalnum() and not ch.isspace():
            return True
    return False

def is_alnum_with_underscore(pass1):
    for ch in pass1:
        if not ch.isalnum() and not ch == "_":
            return False
    return True

def has_number(pass1):
    for ch in pass1:
        if ch.isdigit():
            return True
    return False

def has_space(pass1):
    for ch in pass1:
        if ch.isspace():
            return True
    return False

def register(cur):
    print('\n **REGISTER** \n')
    #Create Username
    while True:
        user_input = input("Enter a username(Must only contain letters, numbers, and underscores(_)): ").strip()
        if user_input == "*":
            return False, ""

        cur.execute('SELECT * FROM users WHERE username ILIKE (%s);', (user_input, ))
        existing = cur.fetchone()
        if is_alnum_with_underscore(user_input) and not existing:
            username = user_input
            break
        else:
            if existing:
                print('Username already taken.')
            print('Please enter a valid username or "*" to go back \n')

    #Create Password
    while True:
        print("Passwords must have:")
        print("\t-At least 1 uppercase \n\t-At least 1 lowercase letter\n\t-At least 1 number\n\t-At least 1 symbol(@#$%^&*)\n\t-No spaces\n\t-At least 8 characters\n")

        #password 1
        pass1 = getpass.getpass("Enter a password: ")
        if pass1 == "*":
            return False, ""
        if not (not has_space(pass1) and has_number(pass1) and has_lower(pass1) and has_upper(pass1) and has_symbol(pass1) and len(pass1) >= 8):
            print('Password does not fulfill requirements. Please enter a valid password or enter "*" to go back \n')
            continue
        
        #password 2
        pass2 = getpass.getpass("Re-enter the password: ")
        if (pass1 == pass2):
            break
        else:
            print('Passwords do not match. Try again or enter "*" to go back\n')

    #Create Database Entry
    password_bytes = pass1.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    hashed_password = hashed_password.decode('utf-8')
    cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))

    return True, username

def login(cur):
    print('\n **LOGIN** \n')
    while True:
        #Inputs
        username = input("Enter Username: ")
        if username == "*":
            return False, ""
        password = getpass.getpass("Enter Password: ")

        #Check if User exists
        cur.execute("SELECT * FROM users WHERE username ILIKE (%s);", (username, ))
        results = cur.fetchone()
        if not results:
            print('User does not exist. Try again or enter "*" to go back\n')
            continue
        
        #Check Password
        password_bytes = password.encode('utf-8')
        if bcrypt.checkpw(password_bytes, results[1].encode('utf-8')):
            return True, results[0]
        else:
            print('Incorrect Password. Try again or enter "*" to go back\n ')

def get_user(cur):
    user = ""
    while True:
        user_input = input("Do you have an account?(Y/N): ").strip().upper()
        if user_input == "Y":
            successful, user = login(cur)
            if(successful):
                print("\n Logged in as:", user)
                break
            else:
                continue
        elif user_input == "N":
            successful, user = register(cur)
            if(successful):
                print("\n Logged in as:", user)
                break
            else:
                continue
        elif user_input == 'Q':
            break
        else:
            print('Please enter a valid option or "Q" to exit \n')
    
    return user
        