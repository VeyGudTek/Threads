from decouple import config
import psycopg2
from authentication import get_user
from commands import process_commands

def main():
    #connect to database
    try:
        conn = psycopg2.connect("dbname={} user='{}' host='{}' password='{}'".format(config("DATABASE"), config("DATABASE_USERNAME"), config("HOST"), config("PASSWORD")))
        print('Connected to Database')
    except:
        print('failed to connect, exiting')
        return
    cur = conn.cursor()

    #Get Current User
    user = get_user(cur)

    #Main Loop
    process_commands(cur, user)
    print()

    #Save changes, End Session
    conn.commit()
    print("All changes Saved.")
    cur.close()
    conn.close()
    print('Done')

if __name__ == "__main__":    
    main()
    