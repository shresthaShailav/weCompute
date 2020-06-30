WeCompute is a platform for sharing compute resources. 
The idea is to allow any computer connected to the internet to execute compute requests on behalf of the requester.
This allows us to utilize idle resources more efficiently(which could belong to us or our friends).

Core : 
The most fundamental unit of weCompute is the weCompute_client(called agent) which needs to be installed on the client machine
To avoid dependency issues, the client itself can be installed with docker.
    

Working : 

We have agents running all over the internet, each with a unique client_id
Each agent has a queue assigned to it which we use the request computate.

We have a server which manages the queue.

Here's how it works : 
The client sends the compute request task through the server to the compute agent.
    Each task contains  :
        environment_code
        requester_id
        task_id
        script_type
        script_code

    For each task the agent receives, the following steps occur : 
        1. Check if the client allows that requester_id to execute on this machine. If No, abort
        2. Use the environment_code to set up the environment where the code will be executed.
                We use Docker to build containers where the code will be executed
                This step is cached to avoid redundancy
        3. Based on the script_type decide how to treat the script_code.
        4. Send the respose of the script(based on script_type) to the requester.

   The requester is responsible for proper allocation & utilization of clients.


to run : 
    docker run --add-host localhost:172.17.0.1 -v /var/run/docker.sock:/var/run/docker.sock -it agent
    (The client needs access to the external socket so that it can orchestrate tasks)

    See : run.py
