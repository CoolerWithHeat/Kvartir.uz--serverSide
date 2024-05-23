from django.test import TestCase
import requests

url = 'http://127.0.0.1:8000/serverdestination/announcement/1/'
data = requests.get(url)
print(data.json())