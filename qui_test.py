import threading 

def hello():
    print('helo')
    timer = threading.Timer(2.0,hello)
    timer.start()
timer = threading.Timer(2.0,hello)
timer.start()