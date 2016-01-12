# -*- coding:utf-8 -*-
import threading
import time


def r(i):
    global lock
    time.sleep(0.5)
    if lock.acquire():
        print u'当前第' + str(i) + u'个线程.'
        lock.release()


def rr(i):
    global lock
    time.sleep(0.5)
    print u'当前第' + str(i) + u'个线程.'

if __name__ == "__main__":
    threadpool = []
    lock = threading.Lock()
    for i in range(1, 20):
        index = i * 100
        t = threading.Thread(target=r, args=[i])
        threadpool.append(t)
    for t in threadpool:
        t.start()
    for t in threadpool:
        t.join()
