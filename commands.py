from psycopg2 import sql
from authentication import get_user
from thread_commands import create_post, delete_post

import math


def print_commands():
    print("Commands:")

    print("\tDisplay:")
    print("\t\thelp - print commands")
    print("\t\tlist - display threads")
    print("\t\tusers - display users")

    print("\tThreads:")
    print("\t\topen [thread id] - view a thread")
    print("\t\tcreate - create a thread")
    print("\t\tdelete [thread id] - delete a thread(Must be the author of the thread)")

    print("\tQuery(commands will display threads):")
    print("\t\tsort [method] - reorder threads by method(title or date)")
    print("\t\tflip - change ordering from ascending to descending and vice versa")
    print("\t\tpage [page number] - go to page of threads(leave empty to go to next page)")
    print("\t\tsearch [query] - search for thread")

    print("\tSystem:")
    print("\t\tdeluser - delete current account")
    print("\t\tlogout - switch users")
    print("\t\tquit - exit program")

def display_threads(posts, user, order_by, ascending, page):
    print("\n{:75}{:>75}".format("THREADS", "Logged in as: " + user))
    print("-" * 150)

    if posts:
        print("{:^5}|{:^50}|{:^50}|{:^12}|{:^30}".format("ID", "Title", "Body", "Date", "User"))
        print("-" * 150)
        for post in posts:
            if len(post[1]) > 45:   title = post[1][:45] + "..."
            else:                   title = post[1]

            if len(post[2]) > 45:   body = post[2][:45] + "..."
            else:                   body = post[2]

            date = f'{post[3].month}/{post[3].day}/{post[3].year}'

            print("{:^5}|{:^50}|{:^50}|{:^12}|{:^30}".format(post[0], title, body, date, post[4]))

        print("-" * 150)
        if ascending:
            asc_text = "ASC"
        else:
            asc_text = "DESC"
        print("{:8}{:>15}{:>5}{}{:>70}{:>5}".format("Sort by:", order_by + ',', asc_text, " " * 47 , "Page", page))
    else:
        print("Nothing to show yet")

def delete_user(cur, user):
    confirmation = input('Are you sure you want to delete your account? Enter "Y" to confirm. Enter anything else to cancel: ').strip().upper()
    if confirmation == "Y":
        cur.execute("DELETE FROM posts WHERE author = %s", (user, ))
        cur.execute("DELETE FROM users WHERE username = %s", (user, ))
        print("Account successfully deleted. ")
        return ""
    else:
        print("Account deletiong canceled.")
        return user

def get_page(cur, page, user_input):
    cur.execute("SELECT COUNT(*) FROM posts;")
    max_pages = math.ceil(cur.fetchone()[0]/10)

    if not user_input and page < max_pages:
        return True, page + 1
    elif not user_input:
        print("You are already on the last page.")
        return False, page
    elif not user_input.isdigit():
        print("Please enter a valid page number.")
        return False, page
    elif int(user_input) > max_pages:
        return True, max_pages
    else:
        return True, int(user_input)
    

def get_order(order_by, user_input):
    if user_input == "title":
        return True, 'title'
    elif user_input == "date":
        return True, 'date_created'
    else:
        print("Please provide a valid sorting method(Title or date) in the format: sort [method].")
        return False, order_by
        


def update_list(cur, order_by, page, ascending):
    #THIS IS NOT FULLY IMPLEMENTED YET
    if ascending:
        cur.execute(sql.SQL("SELECT * FROM posts ORDER BY {} ASC LIMIT 10 OFFSET %s;").format(sql.Identifier(order_by)), ((page - 1) * 10, ))
    else:
        cur.execute(sql.SQL("SELECT * FROM posts ORDER BY {} DESC LIMIT 10 OFFSET %s;").format(sql.Identifier(order_by)), ((page - 1) * 10, ))
    return cur.fetchall()

def process_commands(cur, user):
    #user not logged in
    if not user:
        return

    #initial settings and display
    page = 1
    ascending = False
    order_by = 'date_created'
    cur.execute(sql.SQL("SELECT * FROM posts ORDER BY {} DESC LIMIT 10 OFFSET %s;").format(sql.Identifier(order_by)), ((page - 1) * 10, ))
    posts = cur.fetchall()
    display_threads(posts, user, order_by, ascending, page)


    while True:
        print()
        if not user:
                break
        user_input = input("Enter a Command: ").strip().lower()

        if user_input == 'help':
            print_commands()
        elif user_input == 'list':
            display_threads(posts, user, order_by, ascending, page)
        elif user_input == 'create':
            create_post(cur, user)
            posts = update_list(cur, order_by, page, ascending)
        elif user_input[:7].strip() == 'delete':
            delete_post(cur, user_input[7:].strip(), user)
            posts = update_list(cur, order_by, page, ascending)
        elif user_input[:5].strip() == "sort":
            success, order_by = get_order(order_by, user_input[5:].strip().lower())
            if success:
                posts = update_list(cur, order_by, page, ascending)
                display_threads(posts, user, order_by, ascending, page)
        elif user_input == "flip":
            ascending = not ascending
            posts = update_list(cur, order_by, page, ascending)
            display_threads(posts, user, order_by, ascending, page)
        elif user_input[:5].strip() == "page":
            success, page = get_page(cur, page, user_input[5:].strip())
            if success:
                update_list(cur, order_by, page, ascending)
                display_threads(posts, user, order_by, ascending, page)
        elif user_input == "deluser":
            user = delete_user(cur, user)
            if not user:
                print()
                user = get_user(cur)
                posts = update_list(cur, order_by, page, ascending)
        elif user_input == 'logout':
            user = get_user(cur)
        elif user_input == 'quit':
            break
        else:
            print('Please enter a valid command(Enter "help" list of valid commands).')