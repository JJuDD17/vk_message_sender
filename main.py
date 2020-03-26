import vk_api
import vk_messages
from time import sleep
import datetime as dt
import os


TOKEN = os.environ.get('VK_TOKEN')
assert TOKEN, 'environment variable VK_TOKEN is absent or empty'
POLL_DELAY = 5
target_ids = [299488530]
messages = ['Чево не спиш? 🌚']
time_intervals = [(dt.time(0, 30), dt.time(5, 20))]


def sub_times(start_time: dt.time, stop_time: dt.time):
    date = dt.date(1, 1, 1)
    datetime1 = dt.datetime.combine(date, start_time)
    datetime2 = dt.datetime.combine(date, stop_time)
    return datetime1 - datetime2


def time_in_range(time, range1, range2=None):
    if isinstance(range1, tuple) or isinstance(range1, list):
        if len(range1) == 2:
            range2 = range1[1]
            range1 = range1[0]
    assert range2, 'range2 is absent nor range1 is iterable'
    assert sub_times(range2, range1) > dt.timedelta(0), 'range1 is bigger than range2'
    return sub_times(time, range1) > dt.timedelta(0) and sub_times(time, range2) < dt.timedelta(0)


def log(*args, sep=' ', end='\n'):
    _args = [dt.datetime.now().strftime('[%d.%m %H:%M:%S]')] + list(args)
    print(*_args, sep=sep, end=end)


def main(vk: vk_api.VkApi):
    assert len(target_ids) == len(messages) == len(time_intervals), \
        'lengths of target_ids, messages and time_intervals are not same'

    if len(target_ids) == 0:
        print('target_ids is empty')
        return

    login = os.environ.get('VK_LOGIN')
    password = os.environ.get('VK_PASSWORD')
    assert login, 'environment variable VK_LOGIN is absent or empty'
    assert login, 'environment variable VK_PASSWORD is absent or empty'
    vk_messages.auth(login, password)
    log('Authenticated')

    while True:
        user_ids = ','.join(map(str, target_ids))
        users = vk.users.get(user_ids=user_ids, fields='online')
        log('Got user ids')

        for user in users:
            if user['online'] == 1:
                user_id = user['id']
                index = target_ids.index(user_id)
                message = messages[index]
                if not time_in_range(dt.datetime.now().time(), time_intervals[index]):
                    log(f'User {user_id} is online but current time is not in the given interval')
                    continue
                # log(f'User {user_id} is online. Message: {message}. Index: {index}')

                vk_messages.send(user_id, message)
                log(f'Sent {message} to user {user_id}')

                target_ids.pop(index)
                messages.pop(index)
                time_intervals.pop(index)
                log(f'Popped index {index} from target_ids, messages and time_intervals')
                log('Now target_ids, messages and time_intervals are', target_ids, messages, time_intervals)

                if len(target_ids) == 0 or len(messages) == 0:
                    log('No messages to send anymore. Returning')
                    return

        log('Completed loop')
        sleep(POLL_DELAY)


if __name__ == '__main__':
    vk_session = vk_api.VkApi(token=TOKEN)
    main(vk_session.get_api())
