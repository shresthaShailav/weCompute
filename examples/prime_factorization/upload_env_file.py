import requests
import os
from util import *


# zipfile containing the application
file_path = '{}/envs/primefactor.zip'.format(os.getcwd())

# host to upload to
server = 'http://localhost:4500'
#server = 'http://<task_server_ipv4_addr>'
url = '{server}/env'.format(server=server)

temp_encrypted_file = '{}/encrypted.zip'.format(os.getcwd())
secret = b'primeFactorEnv'
encrypt_file('blowfish_CBC', secret, file_path, temp_encrypted_file)

with open(temp_encrypted_file, 'rb') as f : 
    file_content = f.read()

dat = {
        'client' : 'DV002',
        'key' : 'primefactor.zip'
    }
response = requests.post(url, data=file_content, headers=dat)
print(response)
print(response.text)

os.remove(temp_encrypted_file)

# after this, the server will host the file in url : 
#{url}/{key}  eg: http://localhost:5000/env/primefactor.zip
