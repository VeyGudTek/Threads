import datetime
import math
import psycopg2

def print_post_commands():
    print("\nPost Commands:\n")

    print("\tDisplay commands:")
    print("\t\thelp - print commands")
    print("\t\tshow - display thread")
    print("\t\tlist - display comments")
    print("\t\tflip - flip ordering of comments(ordered by date)")
    print("\t\tpage [page number] - go to page of comments(leave empty to go to next page)")

    print("\tReply commands:")
    print("\t\tcomment [(optional) ID] - comment to post, or comment to comment with ID")
    print("\t\tdelete [ID] - deletes comment(must be author of comment)")
    
    print("\tback - exit post")

def has_letter(text):
    for ch in text:
        if ch.isalpha():
            return True
    return False

def create_post(cur, user):
    print('\n CREATE POST \n')
    
    #Create Title
    while True:
        title = input("Enter a title(must contain at least one character): ")
        if title == "*":
            print("Post creation canceled.")
            return
        elif has_letter(title):
            break
        else:
            print('Please enter a valid title or enter "*" to exit post creation.')

    #Create Body
    while True:
        body = input("Enter your text body(must contain at least one character): ")
        if body == "*":
            print("Post creation canceled.")
            return
        elif has_letter(body):
            break
        else:
            print('Please enter a valid text body or enter "*" to exit post creation.')

    current_date = datetime.datetime.today()

    #Confirmation
    confirmation = input('Enter "Y" to confirm the creation of post: ' + title + '. Enter anything else to cancel: ').strip().upper()
    if not confirmation == "Y":
        print("Post creation canceled.")
        return

    #Post Creation
    cur.execute("INSERT INTO posts (title, body, date_created, author) VALUES (%s, %s, %s, %s);", (title, body, current_date, user))
    print('Post Created.')

def delete_post(cur, id, user):
    if not id:
        print("Please include the id of the post you want to delete in the format: delete [id]")
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
        print("Post creation canceled.")
        return

    cur.execute('DELETE FROM posts WHERE id = %s', (id, ))
    print("Post successfully deleted.")

def view_post(post):
    #print header
    print()
    print(post[1])
    date_text = f'{post[3].month}/{post[3].day}/{post[3].year}'
    print("{:35}{:>20}".format("By: " + post[4], "Created: " + date_text))
    print("-" * 55)

    num_rows = math.ceil(len(post[2])/55)
    num_character = 0
    for i in range(num_rows):
        print(post[2][num_character:num_character+50])
        num_character += 50

def create_comment(cur, post_id, user, comment_id):
    #Check User input
    if comment_id and not comment_id.isdigit():
        print(f"{comment_id} is not a valid id.")
        return
    elif comment_id:
        comment_id = int(comment_id)
        cur.execute("SELECT * FROM comments WHERE id = %s AND post_id = %s", (comment_id, post_id))
        parent = cur.fetchone()
        if not parent:
            print(f'There is no comment with id {comment_id}.')
            return

    #Get comment Body
    print('\n CREATE comment \n')
    while True:
        body = input("Enter comment text(must contain at least one character): ")
        if body == "*":
            print("Comment creation canceled.")
            return
        elif has_letter(body):
            break
        else:
            print('Please enter a valid comment text or enter "*" to exit comment creation.')

    #Create comment
    current_date = datetime.datetime.today()
    if comment_id:
        cur.execute('INSERT INTO comments (post_id, parent_id, author, body, date_created) VALUES (%s, %s, %s, %s, %s);', (post_id, comment_id, user, body, current_date))
    else:
        cur.execute('INSERT INTO comments (post_id, author, body, date_created) VALUES (%s, %s, %s, %s);', (post_id, user, body, current_date))
    print('comment Created.')



def process_post_commands(cur, id, user):
    #Check if ID is Valid
    if not id:
        print("Please include the id of the post you want to view in the format: open [id]")
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

    #Print initial display
    view_post(post)

    while True:
        print()
        user_input = input(f"(Post {id})Enter a Command: ").strip().lower()

        if user_input == 'show':
            view_post(post)
        elif user_input == 'help':
            print_post_commands()
        elif user_input[:8].strip() == 'comment':
            create_comment(cur, id, user, user_input[8:].strip())
        elif user_input == 'back':
            break
        else:
            print('Please enter a valid command(Enter "help" list of valid commands).')
