from threading import Thread, Lock

threadLock = Lock()
a = 0

def function(arg):
    threadLock.acquire()
    global a
    for _ in range(arg):
        a += 1
    threadLock.release()


def main():
    threads = []
    for i in range(5):
        thread = Thread(target=function, args=(1000000,))
        thread.start()
        threads.append(thread)

    [t.join() for t in threads]
    print("----------------------", a)

if __name__ == "__main__":
    main()
