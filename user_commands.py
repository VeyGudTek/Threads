from psycopg2 import sql
import math

def print_user_commands():
    print("\nUser Commands:\n")

    print("\thelp -                   print commands")
    print("\tlist -                   display threads")
    print("\tflip -                   change ordering from ascending to descending and vice versa")
    print("\tpage [page number] -     go to page of threads(leave empty to go to next page)")
    print("\tsearch [query] -         search for user")
    print("\tclr -                    removes searchusers query")
    print("\tback -                   exit users interface")

def display_users(users, users_page, users_ascending, users_query):
    print("\n{:^35}".format('USERS'))
    print("-" * 35)

    if users_query:
        print(f"Search: {users_query}")
        print("-" * 35)
    
    for user in users:
        print("{:^35}".format(user[0]))
    
    print("-" * 35)
    if users_ascending:
            asc_text = "ASC"
    else:
            asc_text = "DESC"
    print("{:8}{:>5}{:>17}{:>5}".format("Sort by:", asc_text, "Page", users_page))

def update_users(cur, users_page, users_ascending, users_query):
    query_text = "%" + users_query + "%"

    if users_ascending:
        cur.execute(sql.SQL("SELECT username FROM users WHERE username ILIKE %s ORDER BY {} ASC LIMIT 10 OFFSET %s;").format(sql.Identifier('username')), (query_text, (users_page - 1) * 10))
    else:
        cur.execute(sql.SQL("SELECT username FROM users WHERE username ILIKE %s ORDER BY {} DESC LIMIT 10 OFFSET %s;").format(sql.Identifier('username')), (query_text, (users_page - 1) * 10))
    return cur.fetchall()

def get_query(cur_query, user_input):
    if len(user_input) > 30:
        print("Usernames do not exceed 30 characters.")
        return False, ''
    elif not cur_query and not user_input:
        print('Search already cleared. If you want to perform a search, provide a query in the format: search [query]')
        return False, user_input
    else:
        return True, user_input

def get_page(cur, page, user_input, query):
    query_text = "%" + query + "%"

    cur.execute('SELECT COUNT(*) FROM users WHERE username ILIKE %s;', (query_text, ))
    max_pages = math.ceil(cur.fetchone()[0]/10)

    if not user_input and page < max_pages:
        return True, page + 1
    elif not user_input:
        print("You are already on (or past) the last page.")
        print("To jump to a certain page, provide a page number in the format: page [page number]")
        print("To jump to the last page, enter an arbitrarily large number for [page number]")
        return False, max_pages
    elif not user_input.isdigit():
        print("Please enter a valid page number.")
        return False, page
    elif int(user_input) < 1:
        print("Please enter a valid page number.")
        return False, page
    elif int(user_input) > max_pages:
        return True, max_pages
    else:
        return True, int(user_input)

def process_user_commands(cur):
    #initial settings and display of user list
    users_ascending = True
    users_page = 1
    users_query = ''
    users = update_users(cur, users_page, users_ascending, users_query)
    display_users(users, users_page, users_ascending, users_query)

    while True:
        print()
        user_input = input("(Users)Enter a Command: ").strip().lower()

        #display
        if user_input == 'help':
            print_user_commands()
        elif user_input == 'list':
            display_users(users, users_page, users_ascending, users_query)
        #query
        elif user_input == "flip":
            users_ascending = not users_ascending
            users = update_users(cur, users_page, users_ascending, users_query)
            display_users(users, users_page, users_ascending, users_query)
        elif user_input[:5].strip() == "page":
            success, users_page = get_page(cur, users_page, user_input[5:].strip(), users_query)
            if success:
                users = update_users(cur, users_page, users_ascending, users_query)
                display_users(users, users_page, users_ascending, users_query)
        elif user_input[:7].strip() == 'search':
            success, users_query = get_query(users_query, user_input[7:].strip())
            if success:
                users_page = 1
                users = update_users(cur, users_page, users_ascending, users_query)
                display_users(users, users_page, users_ascending, users_query)
        elif user_input == 'clr':
            from_user = ''
            users_query = ''
            users_page = 1
            users = update_users(cur, users_page, users_ascending, users_query)
            display_users(users, users_page, users_ascending, users_query)
        elif user_input == 'back':
            break
        else:
            print('Please enter a valid command(Enter "help" list of valid commands).')