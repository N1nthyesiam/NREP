import requests, time

proxy = {
    "http": "http://localhost:8080",
    "https": "http://localhost:8080"
    }

tests_count = 20

sess = requests.Session()

t1 = time.time()
sess.get("https://www.google.com/", proxies=proxy)
t1 = time.time()-t1

t2 = time.time()
sess.get("https://www.google.com", proxies=proxy)
t2 = time.time()-t2

sess = requests.Session()

t3 = time.time()
sess.get("https://www.google.com")
t3 = time.time()-t3

t4 = time.time()
sess.get("https://www.google.com")
t4 = time.time()-t4

print(f"With NREP (includes handshake): {t1} s")
print(f"With NREP (no handshake): {t2} s")
print(f"Without NREP (includes handshake): {t3} s")
print(f"Without NREP (no handshake): {t4} s")