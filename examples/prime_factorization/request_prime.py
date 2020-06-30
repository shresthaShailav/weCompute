import requests 
import time
import os
from pprint import pprint

# The following illustrates and example of how a requester will 
# request for compute from agents running throughout the internet.
# 
# The requester is responsible for breaking down a problem into small tasks.
# The requester is also responsible for providing Docker build information 
#     (so that agents can build the task and then execute the code
# The requester is then responsible for sending request to multiple clients running over the internet
# 
# The clients, upon receiving the task will build the image and then return the response back to the requester.
# 
# Currently, we can use the TaskServer to send and receive tasks
# 
# 
# The following Code illustrates a requester, breaking down a prime factorization problem 
#     into small independent tasks and then requesting agents to solve them in a distributed manner.
# 
# See : 
#     envs/primefactor.zip
#     upload_env_file.py

server = 'http://localhost:4500'
#server = 'http://<task_server_ipv4_addr>
url = '{server}/task'.format(server=server)
self_client_id = 'DV_9999_'

headers = {
        'client' : 'Test_DV9999',
        'API_KEY' : 'NoKEY'
        }

if __name__ == '__main__' : 
    start_time = time.time()

    # get active peers 
    peer_endpoint = '{server}/peers'.format(server=server)
    params = {'id' : self_client_id}
    response = requests.get(peer_endpoint, headers=headers).json()
    peer_list = response['peers']
    if len(peer_list) == 0 : 
        print("No peers available")
        exit()


    # get prime_numbers
    primes = []
    with open('random_numbers.txt', 'r') as f : 
        for line in f : 
            primes.append(line.strip('\n'))
    primes = primes

    # generate task and distribute them among all peers
    task_prefix = '{timestamp}_factorizeReq'.format(timestamp=int(time.time()))
    for count, prime_num in enumerate(primes) :
        peer = peer_list[count % len(peer_list)]

        task = {
            'requester_id' : self_client_id,
            'target_id' : peer,
            'task_id' : '{prefix}-{Id}'.format(prefix=task_prefix, Id=count),
            'instr_code' : 1,
            'env_code' : 1,

            'instr_cmd' : 'python3 prime.py {}'.format(prime_num),

            #'env_url' : '{http://localhost:5000}/env/primefactor.zip',
            'env_url' : '{}/env/primefactor.zip'.format(server),
            'env_encryption' : 'blowfish_CBC',
            'env_compression' : 'zip',
            'env_secret' : 'primeFactorEnv',

            'use_cache' : True
            }

        task_endpoint = '{server}/task'.format(server=server)
        response = requests.post(task_endpoint, json=task)

    # wait for results from peers and print them
    expected_reply_count = len(primes)
    task_endpoint = '{server}/task'.format(server=server)
    params = {'id' : self_client_id}
    remaining = expected_reply_count
    wt_timeout = time.time()
    while remaining : 
        # keep querying until all replies are received
        try : 
            response= requests.get(task_endpoint, params=params).json()
            if response['status'] == 'success' : 
                if response['count'] == 0 : 
                    time.sleep(0.5) # nothing to perform
                    #print("reached")
                    if time.time() - wt_timeout > 10 : 
                        break
                    continue
                else :
                    #print("got task")
                    for task in response['tasks'] : 
                        # only process task with relevant task id
                        #print(task) #
                        if task['task_id'].startswith(task_prefix) : 
                            Id = int(task['task_id'][len(task_prefix+'-'):])
                            print(Id, task['response'])
                            remaining = remaining - 1
                            wt_timeout = time.time()
            if response['status'] == 'failure' : 
                raise Exception("Server returned failure. unable to retrieve task")
        except Exception as e :
            print("Raised error {}:{}".format(e.__class__.__name__, str(e)))
            pass

    end_time = time.time()

    print("elapsed : {}".format(end_time - start_time))
