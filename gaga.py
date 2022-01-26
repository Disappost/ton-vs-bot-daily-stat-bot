import datetime
import os
import time
import traceback

import psycopg2
import telegram

from constants import *

SHIT_COUNTER = 0
separator = '\n\n' + '-' * 64 + '\n\n'


def send_stat(cur, day):
    cur.execute(
        '''
            select
                count(*)
            from
                history
            where
                date("timestamp") = %s
                and "type" = 'bot_action'
                and column_0 = 'open_user'
                and user_id not in (
                1168253329,
                -- DG
                402879150,
                -- F
                193824343
                -- Tolya
                )
        ''',
        [day]
    )
    query_result = cur.fetchone()
    open_users = query_result[0]

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
        [day]
    )
    query_result = cur.fetchone()
    new_users = query_result[0]

    if heroku:
        token = os.environ['bot_token']
    else:
        token = __import__('gag_secrets').bot_token

    bot = telegram.Bot(token)

    message = '{}\n' \
              'open users: {}\n' \
              'new users: {}'.format(
        day,
        open_users,
        new_users
    )

    bot.send_message(channel_chat_id, message)


def main():
    passed_set = set()

    while True:
        day = datetime.date.today() - datetime.timedelta(days=1)

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
                                date("timestamp") = %s
                                and "type" = 'bot_action'
                                and column_0 = 'daily_stat'
                        ''',
                        [day]
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
                                'bot_action',
                                'daily_stat'
                                )
                            ''',
                            [day]
                        )
                        con.commit()

                    passed_set.add(day)

        time.sleep(sleep_timeout)


def gaga():
    global SHIT_COUNTER

    while True:
        try:
            main()
            sleep(3)
        except:
            shit_message = 'SHIT...\n' \
                           'SHIT_COUNTER: {}\n' \
                           'time: {}\n' \
                           '\n' \
                           '{}'.format(
                SHIT_COUNTER,
                datetime.datetime.utcnow(),
                traceback.format_exc()
            )
            print(shit_message + separator)
            time.sleep(2 ** SHIT_COUNTER)
            SHIT_COUNTER += 1


gaga()
