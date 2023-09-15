import math

def get_page(cur, page, user_input, query, from_user):
    query_text = "%" + query + "%"
    from_user_text = from_user if from_user else "%%"

    cur.execute('SELECT * FROM posts WHERE title ILIKE %s and author ILIKE %s;', (query_text, from_user_text))
    max_pages = math.ceil(len(cur.fetchall())/10)

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

def get_query(cur_query, user_input):
    if len(user_input) > 65:
        print("Query is too long.")
        return False, ''
    elif not cur_query and not user_input:
        print('Search already cleared. If you want to perform a search, provide a query in the format: search [query]')
        return False, user_input
    else:
        return True, user_input

def get_from_user(cur, cur_from_user, user_input):
    if not user_input and not cur_from_user:
        print('User already cleared. If you want to filter by user, provide a user in the format: fromuser [user]')
        return False, user_input
    elif not user_input:
        return True, user_input

    cur.execute('SELECT username FROM users WHERE username ILIKE %s', (user_input, ))
    results = cur.fetchone()

    if results:
        return True, results[0]
    else:
        print(f'No user called "{user_input}"')
        return False, ''
    
    
