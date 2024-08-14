"""Sample function use for postgres.postgresdb PostgresDB class
Simply run $ python sample_postgres_code.py to interact with the database
"""

from postgres.postgresdb import PostgresDB


def sample_postgres_code():
    # creates a PostgresDB object
    postgressconn = PostgresDB()

    # creates trips and messages table
    #   do nothing if those two tables already existed.
    postgressconn.create_table()

    # DOESN'T WORK YET! Suppose to get all tables
    postgressconn.get_tables()

    # create a trip
    travel_preferences = "This is an all boys trip. Focus on eating and dining."
    trip_id = postgressconn.create_trip_to_db(
                                    destination="Tokyo,Japan",
                                    days_num="5",
                                    travelers_num="4",
                                    budget="$10,000",
                                    travel_preferences=travel_preferences)
    print(trip_id)

    # predefined prompts
    ITINERARY_JSON = {
        "time": "string",
        "location": "string",
        "activity": "string",
        "average duration": "number",
        "cost": "number"
    }

    PROMPT_ITINERARY = """You are a professional vacation planner helping users
                        plan trips abroad. You will recommend hotels,
                        attractions, restaurants, shopping area, natural sites
                        or any other places that the user requests. You will
                        plan according to the budget and vacation length given
                        by the user. You will present the result in a format of
                        detailed itinerary of each day, begin from day 1 to the
                        last day."""

    message = ("Plan me a 5 days trip to Tokyo,Japan. "
               "This is for a party of 4 adults aging "
               "from 35-38. We are interested in visiting shopping "
               "area, enjoying local food, with a one or two night "
               "life. We will strictly stay in Tokyo,Japan. Budget should "
               "be $10,000 per person without airfare, but include "
               "hotels, meals and other expenses. "
               "Use the following json format with this schema: "
               f"{ITINERARY_JSON} where time is based on 12 hour clock, cost "
               "is a dollar amount, and "
               "average duration is in hours. It will be housed within this "
               """structure " "Day 1": [] " """
               "We will be leaving from New York, USA. This is an all boys "
               "trip. Focus on eating and dining.")

    # create new messages to 'messages' table
    postgressconn.create_message_to_db(trip_id=1,
                                       role="system",
                                       content_type="text",
                                       content_text=PROMPT_ITINERARY)

    postgressconn.create_message_to_db(trip_id=1,
                                       role="user",
                                       content_type="text",
                                       content_text=message)

    # retrieve chat history of a trip_id from 'messages' table
    chat_history = postgressconn.get_chat_history(trip_id=1)
    print(chat_history)

    # retrieve all trips from the 'trips' table
    result = postgressconn.get_all_trips()
    for row in result:
        print(row)

    postgressconn.close_db_connection()

    # DELETE (drop) a table ***USE WITH CARE***
    postgressconn.drop_table("trips")

    # CLEAR (truncate) a table ***USE WITH CARE***
    postgressconn.truncate_table("trips")


def run():
    # creates a PostgresDB object
    postgressconn = PostgresDB()

    #postgressconn.drop_table()

    #postgressconn.create_table()

    postgressconn.create_user_to_db(
        id='test_user_id',
        provider='test_provider',
        access_token='test_access_token',
        first_name='John',
        last_name='Doe',
        email='john_doe@gmail.com',
        url='john_doe.com'
    )


    postgressconn.close_db_connection()


if __name__ == '__main__':
    run()