import random
import string
import datetime

username = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
time1 = datetime.datetime.now()
print('0')
print(username)
print(password)
print(password)
print('exit')
time2 = datetime.datetime.now()
