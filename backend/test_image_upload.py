import urllib.request
import json
import io
from PIL import Image

img = Image.new('RGB', (200, 200), color=(73, 109, 137))
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='PNG')
img_bytes = img_byte_arr.getvalue()

req = urllib.request.Request('http://127.0.0.1:8000/api/v1/auth/login', data=json.dumps({'email':'student@sih.gov.in','password':'password123'}).encode(), headers={'Content-Type':'application/json'})
resp = json.loads(urllib.request.urlopen(req).read().decode())
token = resp['access_token']

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
content_disposition = 'Content-Disposition: form-data; name="file"; filename="sample_resume.png"\r\n'
content_type = 'Content-Type: image/png\r\n\r\n'

body = (f'--{boundary}\r\n' + content_disposition + content_type).encode() + img_bytes + f'\r\n--{boundary}--\r\n'.encode()

req_upload = urllib.request.Request('http://127.0.0.1:8000/api/v1/students/resume', data=body, headers={
    'Content-Type': f'multipart/form-data; boundary={boundary}',
    'Authorization': f'Bearer {token}'
})

try:
    res_upload = json.loads(urllib.request.urlopen(req_upload).read().decode())
    print('Image Upload Status Success:', res_upload['message'])
except urllib.error.HTTPError as e:
    print('HTTP 400 Error Body:', e.read().decode())
