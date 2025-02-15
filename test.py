import requests
import json

url = "https://google.serper.dev/images"

payload = json.dumps({
  "q": "AI trend",
  "gl": "kr",
  "tbs": "qdr:w"
})
headers = {
  'X-API-KEY': 'ce1727a0e4a3008e94a37fee9311d3307e081c18',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)


import requests
import json

url = "https://google.serper.dev/search"

payload = json.dumps({
  "q": "AI trend",
  "tbs": "qdr:w"
})
headers = {
  'X-API-KEY': 'ce1727a0e4a3008e94a37fee9311d3307e081c18',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)