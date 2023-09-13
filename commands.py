import psycopg2
from psycopg2 import sql
from authentication import get_user
import datetime

def has_letter(text):
    for ch in text:
        if ch.isalpha():
            return True
    return False

def print_commands():
    print("Commands:")
    print("\thelp - print commands")
    print("\tview [thread id] - open a thread")
    print("\tcreate - create a thread")
    print("\tdelete [thread id] - delete a thread(Must be the author of the thread)")
    print("\tsort [method] - reorder threads by method(title or date)")
    print("\tpage [page number] - go to page of threads(leave empty to go to next page)")
    print("\tsearch [query] - search for thread")
    print("\tlogout - switch users")
    print("\tquit - exit program")

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
        print("-" * 150)
        print("Nothing to show yet")

def create_post(cur, user):
    print('\n CREATE POST \n')
    
    #Create Title
    while True:
        title = input("Enter a title(must contain at least one character): ")
        if title == "*":
            print("Post creation canceled.\n")
            return
        elif has_letter(title):
            break
        else:
            print('Please enter a valid title or enter "*" to exit post creation.\n')
    print()

    #Create Body
    while True:
        body = input("Enter your text body(must contain at least one character): ")
        if body == "*":
            print("Post creation canceled.\n")
            return
        elif has_letter(body):
            break
        else:
            print('Please enter a valid text body or enter "*" to exit post creation.\n')
    print()

    current_date = datetime.date.today()

    #Confirmation
    confirmation = input('Enter "Y" to confirm the creation of post: ' + title + '. Enter anything else to cancel: ').strip().upper()
    if not confirmation == "Y":
        print("Post creation canceled.\n")
        return

    #Post Creation
    cur.execute("INSERT INTO posts (title, body, date_created, author) VALUES (%s, %s, %s, %s);", (title, body, current_date, user))
    print('Post Created.\n')

def delete_post(cur, id, user):
    if not id:
        print("Please enter a valid id of the post you want to delete")
        return
    if not id.isdigit():
        print(id, "is not a valid id")
        return
    id = int(id)

    cur.execute('SELECT * FROM posts WHERE id = %s', (id, ))
    post = cur.fetchone()
    if not post:
        print('There is no post with id:', id)
        return
    
    if not post[4] == user:
        print('You are not the author or this post.')
        return

    confirmation = input('Enter "Y" to confirm the deletion of post: ' + post[1] + '. Enter anything else to cancel: ').strip().upper()
    if not confirmation == 'Y':
        print("Post creation canceled.\n")
        return

    cur.execute('DELETE FROM posts WHERE id = %s', (id, ))
    print("Post successfully deleted.")
        

    

def process_commands(cur, user):
    page = 0
    order_by = 'date'
    while True:
        #user not logged in
        if not user:
            break

        cur.execute(sql.SQL("SELECT * FROM posts ORDER BY {} LIMIT 10 OFFSET %s;").format(sql.Identifier('author')), (page * 10, ))
        posts = cur.fetchall()

        display_threads(posts, user)
        print()

        user_input = input("Enter a Command: ").strip()

        if user_input == 'help':
            print_commands()
        elif user_input == 'create':
            create_post(cur, user)
        elif user_input[:7].strip() == 'delete':
            delete_post(cur, user_input[7:].strip(), user)
        elif user_input == 'logout':
            user = get_user(cur)
        elif user_input == 'quit':
            break
        else:
            print('Please enter a valid command(Enter "help" list of valid commands).\n')