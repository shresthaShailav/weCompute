import docker 
import sys

# An illustration of how any client which has docker installed could run the weCompute_agent
# We simply pull the image from some repository, and provide them access to external socket and we are done.
# Caveat : Providing access to external socket is a risky step.

client = docker.from_env()

if __name__ == "__main__" : 

    #self_id = 'DV_0011'
    host = 'http://localhost:4500'
    host = 'http://3.6.89.92'
    try : 
        self_id = sys.argv[1]
    except : 
        print("usage : python3 run.py <client_id> <password>")
        exit()

    params = {
            'image' : 'shailav/images:cclient',
            'volumes' : {
                    '/var/run/docker.sock' : {
                        'bind' : '/var/run/docker.sock',
                        'mode' : 'rw'
                        }
                    },
            'environment' : {
                    'HOST' : host,
                    'SELF_ID' : self_id
                    },
            'extra_hosts' : {
                    'localhost' : '172.17.0.1'
                    },
            'detach' : True
        }

    # remove active container if any
    active_containers = client.containers.list()
    for c in active_containers : 
        if 'client' in str(c.image) : 
            if self_id in str(c.exec_run('printenv SELF_ID').output).strip('\n'): 
                c.kill()
                print("killed : {}".format(c))

    # run container
    container = client.containers.run(**params)

    # print logs
    for log in container.logs(stream=True) :
        print(log)
