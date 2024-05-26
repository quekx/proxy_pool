from datetime import datetime

format = "%Y-%m-%d %H:%M:%S"

def sort_key(x):
    return int(x['use_count']) if x['use_count'] else 1

if __name__ == '__main__':
    # time = datetime.now().strftime(format)
    time = '2022-02-20 07:00:13'
    print(time)

    time2 = datetime.now().strftime(format)
    print(time2)

    delta = datetime.strptime(time2, format) - datetime.strptime(time, format)
    print(delta)
    print(delta.days)
    print(delta.seconds)

    delta = datetime.strptime(time, format) - datetime.strptime(time2, format)
    print(delta)
    print(delta.days)
    print(delta.seconds)
    # x = {'c': 1}
    # print('a' in x)
    # print('c' in x)
    # print(sort_key(x))

    t1 = "2024-05-26 14:00:00"
    t2 = "2024-05-26 15:00:00"
    print(t1 < t2)

    pass


