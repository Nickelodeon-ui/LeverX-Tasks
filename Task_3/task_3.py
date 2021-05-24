from threading import Thread, Lock
import time
import concurrent.futures


def function(arg, a):
    for _ in range(arg):
        a += 1
    return a

def main():
    start_time = time.time()
    a = 0
    threads = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(5):
            future = executor.submit(function, 1000000, a)
            threads.append(future)
        for thread in concurrent.futures.as_completed(threads):
            a += thread.result()
            
    print("----------------------", a)
    print("Result time:", time.time() - start_time)

if __name__ == "__main__":
    main()
