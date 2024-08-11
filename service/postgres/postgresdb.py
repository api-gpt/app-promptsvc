""" PostgresDB class that interacts with Postgres database.
    Used by prompt-svc main.py
"""

import postgres.SQLcmd as SQLcmd
import psycopg2, os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ['DATABASE_URL']


def init_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        # can also change to auto commit (no need for cur.commit
        #   after SQL execution)
        # conn.autocommit = 1
        print("Postgres: successfully connected to database")
        return conn

    except (Exception, psycopg2.DatabaseError) as error:
        print(f'Postgres: Could not connect to the Database: {error}.')


class PostgresDB():

    def __init__(self) -> None:
        self.conn = init_db_connection()

    # close connection with Postgres
    def close_db_connection(self):
        # close the communication with the database server
        #   by calling the close()
        if self.conn is not None:
            self.conn.close()
            print('Postgres: Database connection closed.')

    # create trips and messages table (only use once)
    def create_table(self):
        try:
            # create a new cursor, with statement will auto close the cursor
            with self.conn.cursor() as cur:
                cur.execute(SQLcmd.create_trips_table)
                print('Postgres: trips table created.')
                cur.execute(SQLcmd.create_messages_table)
                print('Postgres: messages table created.')
                # commit changes to database
                self.conn.commit()
            return
        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Postgres: Could not create tables: {error}.')

    # list all tables in database
    def get_tables(self):
        with self.conn.cursor() as cur:
            cur.execute(SQLcmd.list_all_tables)
            # get the generated id back
            rows = cur.fetchone()
            if rows:
                print(rows)
                rows = cur.fetchone()
        return

    # create a new trip to trips table
    def create_trip_to_db(self, destination, days_num, travelers_num, budget,
                          travel_preferences, user_id=None):
        try:
            # create a new cursor, with statement will auto close the cursor
            with self.conn.cursor() as cur:
                if user_id is not None:
                    # execute the INSERT statement
                    cur.execute(SQLcmd.insert_trips_table,
                                (user_id, destination, days_num,
                                    travelers_num, budget, travel_preferences))

                else:
                    # execute the INSERT statement
                    cur.execute(SQLcmd.insert_trips_table_no_user_id,
                                (destination, days_num, travelers_num,
                                    budget, travel_preferences))

                # commit the changes to the database
                self.conn.commit()

                # get the generated id back
                rows = cur.fetchone()
                if rows:
                    trip_id = rows[0]

                print('Postgres: create trip successful.')

                return trip_id

        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Postgres: Could not insert trip to the Database: {error}.')

    # create a new message to messages table
    def create_message_to_db(self, trip_id, role, content_type,
                             content_text, message_category):
        try:
            # create a new cursor, with statement will auto close the cursor
            with self.conn.cursor() as cur:

                # execute the INSERT statement
                cur.execute(SQLcmd.insert_messages_table,
                            (trip_id, role, content_type,
                             content_text, message_category))

                # commit the changes to the database
                self.conn.commit()

                # get the generated id back
                rows = cur.fetchone()
                if rows:
                    message_id = rows[0]

                print(f"Postgres: New {message_category} message created.")

                return message_id

        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Could not insert message to the Database: {error}.')

    # retrieve a chat history
    # returns an array of message_object(s)
    def get_chat_history(self, trip_id):
        try:
            # create a blank array of message_object
            chat_history = []
            # create a new cursor, with statement will auto close the cursor
            with self.conn.cursor() as cur:
                # fetch all messages with trip_id from 'messages' table
                cur.execute(SQLcmd.select_message, (str(trip_id)))

                """Construct chat_history by appending each row of result.
                Process the result set returned by the SELECT statement using
                fetchone(). fetchone() fetches the next row in the result set,
                returns NONE when no more row is available"""
                row = cur.fetchone()
                while row is not None:
                    # turn each row of data into message_object
                    message_object = {
                        "role": row[0],
                        "content": [
                            {
                                "type": row[1],
                                "text": row[2]
                            }
                        ]
                    }
                    # then append to chat_history
                    chat_history.append(message_object)
                    row = cur.fetchone()

                print("Postgres: select chat-history message succesful.")

            return chat_history

        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Postgres: Could not select message: {error}.')

    # retrieve the most recent itinerary created by GPT
    # returns a string
    def get_recent_itinerary(self, trip_id):
        try:
            with self.conn.cursor() as cur:
                # fetch all messages with trip_id from 'messages' table
                cur.execute(SQLcmd.select_recent_itinerary, (str(trip_id), ))

                """Construct chat_history by appending each row of result.
                Process the result set returned by the SELECT statement using
                fetchone(). fetchone() fetches the next row in the result set,
                returns NONE when no more row is available"""
                row = cur.fetchone()
                recent_itinerary = row[2]
                print('Postgres: select message successful.')
            return recent_itinerary

        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Postgres: Could not select message: {error}.')

    # retrieve all trips
    def get_all_trips(self):
        try:
            result = []
            with self.conn.cursor() as cur:
                cur.execute(SQLcmd.select_all_trips, ())
                print("Postgres: select trips successful.")
                row = cur.fetchone()
                while row is not None:
                    result.append(row)
                    row = cur.fetchone()

            return result

        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Postgres:  Could not select trips: {error}.')

    # retieve a trip
    # returns a library
    def get_trip(self, trip_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute(SQLcmd.select_trip, (str(trip_id), ))
                print("Postgres: select trip successful.")
                row = cur.fetchone()
                respond = {
                    "trip_id": row[0],
                    "user_id": row[1],
                    "destination": row[2],
                    "days_num": row[3],
                    "travelers_num": row[4],
                    "budget": row[5],
                    "travel_preference": row[6]
                }
            return respond

        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Postgres: Could not select trips: {error}.')

    # delete (drop) trips and messages table and all their data
    def drop_table(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute(SQLcmd.drop_trips_table)
                print("Postgres: trips table dropped.")
                cur.execute(SQLcmd.drop_messages_table)
                print("Postgres: message table dropped.")

                # commit the changes to the database
                self.conn.commit()
            return

        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Postgres: Could not drop table: {error}.')

    # clear (truncate) a table of all its data
    def truncate_table(self, table_name):
        try:
            with self.conn.cursor() as cur:
                cur.execute(SQLcmd.truncate_table, (table_name,))
                print(f"Postgres: {table_name} truncated.")
                # commit the changes to the database
                self.conn.commit()
            return
        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Postgres: Could not truncate table: {error}.')

    # get all trip of a user
    def get_trip_from_user(self, user_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute(SQLcmd.select_trip_from_user, (str(user_id), ))
                print("Postgres: select trip successful.")
                history = []
                row = cur.fetchone()
                while row is not None:
                    # turn each row of data into message_object
                    trip_object = {
                        "trip_id": row[0],
                        "user_id": row[1],
                        "destination": row[2],
                        "days_num": row[3],
                        "travelers_num": row[4],
                        "budget": row[5],
                        "travel_preference": row[6]
                    }
                    # then append to chat_history
                    history.append(trip_object)
                    row = cur.fetchone()

                print("Postgres: select trips from a user succesful.")

            return history

        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Postgres: Could not select trips: {error}.')

    # insert user
    def create_user_to_db(self, id, provider, access_token, first_name, last_name, email, url):
        try:
            # create a new cursor, with statement will auto close the cursor
            with self.conn.cursor() as cur:

                # execute the INSERT statement
                cur.execute(SQLcmd.insert_users_table,
                            (id, provider, access_token,
                             first_name, last_name, email, url))

                # commit the changes to the database
                self.conn.commit()

                # get the generated id back
                rows = cur.fetchone()
                if rows:
                    user_id = rows[0]

                print(f"Postgres: New user created.")

                return user_id

        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Could not insert user to the Database: {error}.')