import redis
import time
import json
import config

redis_endpoint = config.redis_endpoint
host, port = redis_endpoint.split(':')
r = redis.Redis(host=host, port=port, db=0, socket_timeout=10)

class Tracker :
    """
        keeps track of the number of clients that are active
        and deletes those that are not
    """

    active_clients_set = 'active_clients'       # sorted set holding the active_clients
    timeout = (10+5)*60*60                      # in seconds (before the client is removed from the active clients set)

    def get_active_clients() : 
        """
            get all the clients that are currently active

            we do this by selecting clients whose scores(timestamp) is not 
                well pass the timestamp cutoff period
        """
        Tracker.clear_inactive_clients()
        alive_clients =  r.zrange(Tracker.active_clients_set, 0, -1) 
        return [client.decode('utf-8') for client in alive_clients]


    def clear_inactive_clients() : 
        """ 
            get rid of all clients who have timed out
            scores are timestamps so we simply remove elements 
                with scores well pass the timestamp cutoff
        """
        inactive_timeout = int(time.time()) - Tracker.timeout
        r.zremrangebyscore(Tracker.active_clients_set, 0, inactive_timeout)
            
         
    def add_active_clients(client_ids) : 
        """
            add client_id to available active clients
            we use the timestamp as the scores so that we can easily remove them later

            client_ids : a list of client id
        """
        current_time = int(time.time())
        mapping = {client_id.encode('utf-8') : current_time for client_id in client_ids}
        r.zadd(Tracker.active_clients_set, mapping)


    def is_active(client_id) : 
        """ 
            returns True if the client is active, else false
        """
        Tracker.clear_inactive_clients()
        client_id = client_id.encode('utf-8')
        return not r.zrank(Tracker.active_clients_set, client_id) is None


    def clear_all_clients() : 
        """
            get rid of all the clients currently active (refresh)
        """
        current_time = int(time.time())
        r.zremrangebyscore(Tracker.active_clients_set,0, current_time)


class InstructionManager : 
    pass


class TaskQueue : 
    """
        Every agent has a queue attached to it

        This is class for that queue management in redis
        The master clients are responsible for populating the instructions

        When the slave completes the instruction, it puts the result of the instruction
            in the stream of the requesting master 

        The client can choose whether to execute the instruction or not
        The server only manages the instruction queue
    """
    def push(queue, instruction) : 
        """
            queue -> the id of the client
            instruction : a dict of instructions
        """
        try : 
            return r.rpush(queue, json.dumps(instruction).encode('utf-8'))
        except : return -1


    def pop(queue) : 
        """
            queue -> the id of the client from which to pop
        """
        try : 
            return json.loads(r.lpop(queue).decode('utf-8'))
        except : 
            return None



if __name__ == '__main__' : 
    #Tracker.add_active_clients(['23ASP', '57'])
    #Tracker.clear_inactive_clients()
    #print(Tracker.get_active_clients())
    #print(Tracker.is_active('57'))
    pass
