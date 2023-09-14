import math

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