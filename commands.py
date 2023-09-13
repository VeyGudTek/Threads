from psycopg2 import sql
from authentication import get_user
from thread_commands import create_post, delete_post


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
    print("\t\tlogout - switch users")
    print("\t\tquit - exit program")

def display_threads(posts, user):
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
    else:
        print("Nothing to show yet")

def update_list(cur, order_by, page):
    #THIS IS NOT FULLY IMPLEMENTED YET
    cur.execute(sql.SQL("SELECT * FROM posts ORDER BY {} DESC LIMIT 10 OFFSET %s;").format(sql.Identifier(order_by)), (page * 10, ))
    return cur.fetchall()

def process_commands(cur, user):
    #user not logged in
    if not user:
        return

    #initial settings and display
    page = 0
    order_by = 'date_created'
    cur.execute(sql.SQL("SELECT * FROM posts ORDER BY {} DESC LIMIT 10 OFFSET %s;").format(sql.Identifier(order_by)), (page * 10, ))
    posts = cur.fetchall()
    display_threads(posts, user)


    while True:
        print()
        user_input = input("Enter a Command: ").strip()

        if user_input == 'help':
            print_commands()
        elif user_input == 'list':
            display_threads(posts, user)
        elif user_input == 'create':
            create_post(cur, user)
            posts = update_list(cur, order_by, page)
        elif user_input[:7].strip() == 'delete':
            delete_post(cur, user_input[7:].strip(), user)
            posts = update_list(cur, order_by, page)
        elif user_input == 'logout':
            user = get_user(cur)
            if not user:
                break
        elif user_input == 'quit':
            break
        else:
            print('Please enter a valid command(Enter "help" list of valid commands).')