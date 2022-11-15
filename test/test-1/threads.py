import threading

i = 0
def func1(i):
    i+=1
    print(i)
def func2(i):
    i+=1
    print(i)

x = threading.Thread(target=func1,args=(i,))
y = threading.Thread(target=func2,args=(i,))

x.start()
x.end()
y.start()
y.end()
