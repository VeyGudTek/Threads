from psycopg2 import sql
from authentication import get_user, delete_user
from thread_commands import create_post, delete_post
from query_commands import get_order, get_page, get_query, get_from_user, get_page_users

def print_commands():
    print("Commands:")

    print("\tDisplay:")
    print("\t\thelp - print commands")
    print("\t\tlist - display threads")
    print("\t\tusers - display users")

    print("\tThreads:")
    print("\t\topen [thread id] -   view a thread")
    print("\t\tcreate -             create a thread")
    print("\t\tdelete [thread id] - delete a thread(Must be the author of the thread)")

    print("\tThread Query(commands will display threads):")
    print("\t\tsort [method] -      reorder threads by method(title or date)")
    print("\t\tflip -               change ordering from ascending to descending and vice versa")
    print("\t\tpage [page number] - go to page of threads(leave empty to go to next page)")
    print("\t\tsearch [query] -     search for thread by title, enter nothing to clear query")
    print("\t\tfrom [user] -        filter threads by user, enter nothing to clear query")
    print("\t\tclr -                removes both search and fromuser query")

    print("\tUser Query(commands will display users):")
    print("\t\tflipusers -                  change ordering from ascending to descending and vice versa")
    print("\t\tpageusers [page number] -    go to page of threads(leave empty to go to next page)")
    print("\t\tsearchusers [query] -        search for user")
    print("\t\tclrusers -                   removes searchusers query")

    print("\tSystem:")
    print("\t\tdeluser -    delete current account")
    print("\t\tlogout -     switch users")
    print("\t\tquit -       exit program")

def display_threads(posts, user, order_by, ascending, page, query, from_user):
    #print header
    print("\n{:75}{:>75}".format("THREADS", "Logged in as: " + user))
    print("-" * 150)
    #print queries
    if query or from_user:
        query_text = query if query else 'None'
        from_user_text = from_user if from_user else 'All'
        print("{:75}{:>75}".format("Search: " + query_text, "From user: " + from_user_text))
        print("-" * 150)
    
    if posts:
        #print posts
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
    print("-" * 150)

     #print filter
    if ascending:
        asc_text = "ASC"
    else:
        asc_text = "DESC"
    print("{:8}{:>15}{:>5}{}{:>70}{:>5}".format("Sort by:", order_by + ',', asc_text, " " * 47 , "Page", page))

def display_users(users, users_page, users_ascending):
    print("\n{:^35}".format('USERS'))
    print("-" * 35)
    
    for user in users:
        print("{:^35}".format(user[0]))
    
    print("-" * 35)
    if users_ascending:
            asc_text = "ASC"
    else:
            asc_text = "DESC"
    print("{:8}{:>5}{:>17}{:>5}".format("Sort by:", asc_text, "Page", users_page))

def update_posts(cur, order_by, page, ascending, query, from_user):
    query_text = "%" + query + "%"
    from_user_text = from_user if from_user else "%%"

    if ascending:
        cur.execute(sql.SQL("SELECT * FROM posts WHERE title ILIKE %s AND author ILIKE %s ORDER BY {} ASC LIMIT 10 OFFSET %s;").format(sql.Identifier(order_by)), (query_text, from_user_text, (page - 1) * 10))
    else:
        cur.execute(sql.SQL("SELECT * FROM posts WHERE title ILIKE %s AND author ILIKE %s ORDER BY {} DESC LIMIT 10 OFFSET %s;").format(sql.Identifier(order_by)), (query_text, from_user_text, (page - 1) * 10))
    return cur.fetchall()

def update_users(cur, users_page, users_ascending):
    if users_ascending:
        cur.execute(sql.SQL("SELECT username FROM users ORDER BY {} ASC LIMIT 10 OFFSET %s;").format(sql.Identifier('username')), ((users_page - 1) * 10, ))
    else:
        cur.execute(sql.SQL("SELECT username FROM users ORDER BY {} DESC LIMIT 10 OFFSET %s;").format(sql.Identifier('username')), ((users_page - 1) * 10, ))
    return cur.fetchall()

def process_commands(cur, user):
    #user not logged in
    if not user:
        return

    #initial settings and display of Threads
    page = 1
    ascending = False
    order_by = 'date_created'
    query = ''
    from_user = ''
    posts = update_posts(cur, order_by, page, ascending, query, from_user)
    display_threads(posts, user, order_by, ascending, page, query, from_user)

    #initial settings of user list
    users_ascending = True
    users_page = 1
    users_query = ''
    users = update_users(cur, users_page, users_ascending)


    while True:
        print()
        if not user:
                break
        user_input = input("Enter a Command: ").strip().lower()

        #display
        if user_input == 'help':
            print_commands()
        elif user_input == 'list':
            posts = update_posts(cur, order_by, page, ascending, query, from_user)
            display_threads(posts, user, order_by, ascending, page, query, from_user)
        elif user_input == 'users':
            display_users(users, users_page, users_ascending)
        #threads
        elif user_input == 'create':
            create_post(cur, user)
        elif user_input[:7].strip() == 'delete':
            delete_post(cur, user_input[7:].strip(), user)
            _, page = get_page(cur, page, str(page), query, from_user)
        #thread query
        elif user_input[:5].strip() == "sort":
            success, order_by = get_order(order_by, user_input[5:].strip().lower())
            if success:
                posts = update_posts(cur, order_by, page, ascending, query, from_user)
                display_threads(posts, user, order_by, ascending, page, query, from_user)
        elif user_input == "flip":
            ascending = not ascending
            posts = update_posts(cur, order_by, page, ascending, query, from_user)
            display_threads(posts, user, order_by, ascending, page, query, from_user)
        elif user_input[:5].strip() == "page":
            success, page = get_page(cur, page, user_input[5:].strip(), query, from_user)
            if success:
                posts = update_posts(cur, order_by, page, ascending, query, from_user)
                display_threads(posts, user, order_by, ascending, page, query, from_user)
        elif user_input[:7].strip() == 'search':
            success, query = get_query(query, user_input[7:].strip())
            if success:
                page = 1
                posts = update_posts(cur, order_by, page, ascending, query, from_user)
                display_threads(posts, user, order_by, ascending, page, query, from_user)
        elif user_input[:5].strip() == 'from':
            success, from_user = get_from_user(cur, from_user, user_input[5:].strip())
            if success:
                page = 1
                posts = update_posts(cur, order_by, page, ascending, query, from_user)
                display_threads(posts, user, order_by, ascending, page, query, from_user)
        elif user_input == 'clr':
            from_user = ''
            query = ''
            page = 1
            posts = update_posts(cur, order_by, page, ascending, query, from_user)
            display_threads(posts, user, order_by, ascending, page, query, from_user)
        #user query
        elif user_input == "flipusers":
            users_ascending = not users_ascending
            users = update_users(cur, users_page, users_ascending)
            display_users(users, users_page, users_ascending)
        elif user_input[:10].strip() == "pageusers":
            success, users_page = get_page_users(cur, users_page, user_input[10:].strip(), users_query)
            if success:
                users = update_users(cur, users_page, users_ascending)
                display_users(users, users_page, users_ascending)
        #system
        elif user_input == "deluser":
            user = delete_user(cur, user)
            if not user:
                print()
                user = get_user(cur)
                if user:                #Reset queries and filters
                    from_user = ''
                    query = ''
                    page = 1
                    users_ascending = True
                    users_page = 1
                    users_query = ''
                    posts = update_posts(cur, order_by, page, ascending, query, from_user)
                    users = update_users(cur, users_page, users_ascending)
                    display_threads(posts, user, order_by, ascending, page, query, from_user)
        elif user_input == 'logout':
            user = get_user(cur)
            if user:                    #Reset queries and filters
                    from_user = ''
                    query = ''
                    page = 1
                    users_ascending = True
                    users_page = 1
                    users_query = ''
                    posts = update_posts(cur, order_by, page, ascending, query, from_user)
                    display_threads(posts, user, order_by, ascending, page, query, from_user)
        elif user_input == 'quit':
            break
        else:
            print('Please enter a valid command(Enter "help" list of valid commands).')