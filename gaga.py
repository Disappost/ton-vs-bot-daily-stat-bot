import datetime
import os
import time
import traceback

import psycopg2
import telegram

import pie
from constants import *

SHIT_COUNTER = 0
separator = '\n\n' + '-' * 64 + '\n\n'


def send_stat(cur, day):
    query = '''
                select
                    count(*)
                from
                    history
                where
                    date("timestamp") = %s
                    and "type" = 'bot_action'
                    and column_0 = 'open_user'
                    and user_id not in ({})
            '''.format(', '.join([str(i) for i in volunteers_ids]))
    cur.execute(
        query,
        (day,)
    )
    query_result = cur.fetchone()
    open_users_count = query_result[0]

    ####

    cur.execute(
        '''
            select
                count(*)
            from
                history
            where
                date("timestamp") = %s
                and "type" = 'bot_action'
                and column_0 = 'new_user'
        ''',
        (day,)
    )
    query_result = cur.fetchone()
    new_users_count = query_result[0]

    ####

    cur.execute(
        '''
            select 
                count(*)
            from
                history
            where 
                date("timestamp") = %s
                and "type" = 'message'
        ''',
        (day,)
    )
    query_result = cur.fetchone()
    messages_count = query_result[0]

    ####

    cur.execute(
        '''
            select 
                count(*)
            from
                history
            where 
                date("timestamp") = %s
                and "type" = 'message'
                and volunteer_id isnull
                and column_2 not like '/%%'
        ''',
        (day,)
    )
    query_result = cur.fetchone()
    messages_from_users_count = query_result[0]

    ####

    if heroku:
        token = os.environ['bot_token']
    else:
        token = __import__('gag_secrets').bot_token

    bot = telegram.Bot(token)

    message = f'{day}\n' \
              f'\n' \
              f'new users: {new_users_count}\n' \
              f'open users: {open_users_count}\n' \
              f'messages: {messages_count}\n' \
              f'messages from users: {messages_from_users_count}\n'

    bot.send_message(channel_chat_id, message)

    ####

    cur.execute(
        '''
            select
                column_1
            from
                history
            where 
                date("timestamp") = %s and 
                "type" = 'bot_action' and
                column_0 = 'close_user'
        ''',
        (day,)
    )
    query_result = cur.fetchall()

    list_of_subject_paths = [i[0] for i in query_result]

    if list_of_subject_paths:
        bytes_of_image = pie.get_pie(list_of_subject_paths, day)

        bot.send_document(
            channel_chat_id,
            document=bytes_of_image,
            filename=f'{day}.png'
        )
    else:
        bot.send_photo(
            channel_chat_id,
            photo='AgACAgIAAxkBAAMDYpjeG0cJ2_F3_eRFyu25iKs-5H8AAr67MRuVUchI8VP48-3WO6sBAAMCAAN5AAMkBA'
        )


def main():
    passed_set = set()

    while True:
        day = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)

        if day in passed_set:
            if comments_in_console:
                print('there is in set')

        else:
            if heroku:
                uri = os.environ['DB_URI']
                sslmode = 'require'
            else:
                uri = __import__('gag_secrets').db_uri
                sslmode = None

            with psycopg2.connect(uri, sslmode=sslmode) as con:
                with con.cursor() as cur:
                    cur.execute(
                        '''
                            select
                                1
                            from
                                history
                            where
                                "timestamp" = %s
                                and "type" = 'daily_stat_bot_action'
                                and column_0 = 'daily_stat'
                        ''',
                        (day,)
                    )
                    query_result = cur.fetchone()

                    if query_result:
                        if comments_in_console:
                            print('there is in db')

                    else:
                        if comments_in_console:
                            print('GAGAGAGAGAGAG    ' + str(day))
                        send_stat(cur, day)

                        cur.execute(
                            '''
                                insert
                                    into
                                    history ("timestamp",
                                    "type",
                                    "column_0")
                                values (%s,
                                'daily_stat_bot_action',
                                'daily_stat'
                                )
                            ''',
                            (day,)
                        )
                        con.commit()

                    passed_set.add(day)

        time.sleep(sleep_timeout)


def gaga():
    global SHIT_COUNTER

    while True:
        try:
            main()
            time.sleep(3)
        except:
            shit_report = f'SHIT...\n' \
                          f'SHIT_COUNTER: {SHIT_COUNTER}\n' \
                          f'time: {datetime.datetime.utcnow()}\n' \
                          f'\n' \
                          f'{traceback.format_exc()}'
            print(shit_report + separator)
            time.sleep(2 ** SHIT_COUNTER)
            SHIT_COUNTER += 1


gaga()
