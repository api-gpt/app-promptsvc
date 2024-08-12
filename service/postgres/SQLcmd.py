create_trips_table = """CREATE TABLE IF NOT EXISTS trips (
                              trip_id SERIAL NOT NULL PRIMARY KEY,
                              user_id VARCHAR(255),
                              destination VARCHAR(255) NOT NULL,
                              days_num VARCHAR(255) NOT NULL,
                              travelers_num VARCHAR(255) NOT NULL,
                              budget VARCHAR(255) NOT NULL,
                              travel_preferences TEXT,
                              FOREIGN KEY(user_id)
                                REFERENCES users(id)
                                ON DELETE CASCADE
                             );"""

create_messages_table = """CREATE TABLE IF NOT EXISTS messages (
                            message_id SERIAL NOT NULL PRIMARY KEY,
                            trip_id INT NOT NULL,
                            role VARCHAR(255) NOT NULL,
                            content_type VARCHAR(255) NOT NULL,
                            content_text TEXT NOT NULL,
                            message_category VARCHAR(255) NOT NULL,
                            FOREIGN KEY(trip_id)
                                REFERENCES trips(trip_id)
                                ON DELETE CASCADE,
                            CONSTRAINT message_pk UNIQUE (message_id, trip_id)
                            );"""

create_profile_table = """CREATE TABLE IF NOT EXISTS profiles (
                            profile_id SERIAL NOT NULL PRIMARY KEY,
                            user_id VARCHAR(255),
                            age INT NOT NULL,
                            travelStyle TEXT NOT NULL,
                            travelPriorities TEXT NOT NULL,
                            travelAvoidances TEXT NOT NULL,
                            dietaryRestrictions TEXT NOT NULL,
                            accomodations TEXT NOT NULL,
                              FOREIGN KEY(user_id)
                                REFERENCES users(id)
                                ON DELETE CASCADE,
                            CONSTRAINT message_pk UNIQUE (profile_id, user_id)
                            );"""

insert_trips_table = """INSERT INTO trips (user_id, destination,
                        days_num, travelers_num, budget, travel_preferences)
                        VALUES(%s, %s, %s, %s, %s, %s)
                        RETURNING trip_id;"""

insert_trips_table_no_user_id = """INSERT INTO trips (destination, days_num,
                            travelers_num, budget, travel_preferences)
                            VALUES(%s, %s, %s, %s, %s)
                            RETURNING trip_id;"""

insert_messages_table = """INSERT INTO messages (trip_id, role, content_type,
                            content_text, message_category)
                            VALUES(%s, %s, %s, %s, %s)
                            RETURNING message_id;"""

insert_profiles_table = """INSERT INTO profiles (profile_id, user_id, age,
                            travelStyle, travelPriorities, travelAvoidances,
                            dietaryRestrictions, accomodations)
                            VALUES(%s, %s, %s, %s, %s, %s, %s)
                            RETURNING profile_id;"""

# returns the entire chat history
select_message = """SELECT role, content_type, content_text, message_category
                    FROM messages
                    WHERE trip_id=%s
                    ORDER BY message_id;"""

# returns only itinerary message where the first row is the most recent
select_recent_itinerary = """SELECT role, content_type, content_text,
                            message_category FROM messages
                            WHERE trip_id=%s AND message_category='ITINERARY'
                            ORDER BY message_id DESC;"""

select_all_trips = """SELECT trip_id, user_id, destination,
                days_num, travelers_num, budget, travel_preferences
                FROM trips ORDER BY trip_id;"""

select_trip = """SELECT trip_id, user_id, destination,
                days_num, travelers_num, budget, travel_preferences
                FROM trips
                WHERE trip_id=%s;"""

select_trip_from_user = """SELECT trip_id, user_id, destination,
                days_num, travelers_num, budget, travel_preferences
                FROM trips
                WHERE user_id=%s
                ORDER BY trip_id;"""

select_profile = """SELECT profile_id, user_id, age,
                travelStyle, travelPriorities, travelAvoidances,
                dietaryRestrictions, accomodations
                FROM profiles
                WHERE user_id=%s;"""

update_profiles_table = """UPDATE profiles
                           SET (age,
                            travelStyle, travelPriorities, travelAvoidances,
                            dietaryRestrictions, accomodations)
                            = (%s, %s, %s, %s, %s, %s)
                            WHERE user_id=%s
                            RETURNING profile_id;"""

# CASCADE means delete all data in other table that references this table
drop_trips_table = """DROP table trips CASCADE;"""

drop_messages_table = """DROP table messages CASCADE;"""

# somehow this doesn't work
list_all_tables = """select * from information_schema.tables
                    where table_schema = 'information_schema'"""

# somehow this doesn't work as variable with %s has qoutes around them
drop_table = """DROP TABLE %s;"""

truncate_table = """TRUNCATE TABLE %s;"""

insert_users_table = """INSERT INTO users (id, provider, access_token,
                        first_name, last_name, email, url)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET 
                        access_token = EXCLUDED.access_token,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        email = EXCLUDED.email,
                        url = EXCLUDED.url
                        RETURNING id;"""
