import requests
import time

while True:
    request = requests.get('http://127.0.0.1:8000/spotify')
    print(request.content)
    time.sleep(1800)
