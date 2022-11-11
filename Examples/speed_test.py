import requests, time, os

proxy = {
    "http": "http://localhost:8080",
    "https": "http://localhost:8080"
    }

tests_count = 10
t1,t2,t3,t4=[],[],[],[]

for _ in range(tests_count):
    t = os.popen("curl -o /dev/null --proxy http://localhost:8080 -s https://www.google.com/ -w %{time_total}\n").read()
    t1.append(float(t))

sess = requests.Session()
sess.get("https://www.google.com/", proxies=proxy)
for _ in range(tests_count):
    t = time.perf_counter()
    sess.get("https://www.google.com", proxies=proxy)
    t = time.perf_counter()-t
    t2.append(t)

for _ in range(tests_count):
    t = os.popen("curl -o /dev/null -s https://www.google.com/ -w %{time_total}\n").read()
    t3.append(float(t))

sess = requests.Session()
sess.get("https://www.google.com")
for _ in range(tests_count):
    t = time.perf_counter()
    sess.get("https://www.google.com")
    t = time.perf_counter()-t
    t4.append(t)

t1 = sum(t1)/len(t1)
t2 = sum(t2)/len(t2)
t3 = sum(t3)/len(t3)
t4 = sum(t4)/len(t4)
p1 = round(t1/t3*100-100,1)
p2 = round(t2/t4*100-100,1)
print(f"With NREP (no piping): {t1}s")
print(f"With NREP (piping): {t2}s")
print(f"Without NREP (first request): {t3}s")
print(f"Without NREP (second request): {t4}s")
print(f"NREP is {abs(p1)} % {'slower' if p1<=0 else 'faster'}")
print(f"NREP (piping) is {abs(p2)} % {'slower' if p2<=0 else 'faster'}")
