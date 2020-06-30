import os
import sys

def get_environ(var, default='__force', cast=str) :
    try : 
        val = cast(os.environ[var])
        return val 
    except : 
        if not default == '__force' : 
            return default
        else :
            raise Exception("ERROR. Environment variable {} missing".format(var))

app_path = get_environ('APP_PATH', os.getcwd())

host = get_environ('HOST')
wait_interval = get_environ('WAIT_INTERVAL', default=30, cast=int)
self_id = get_environ('SELF_ID')

# file paths
env_directory = '{app_path}/_envs/'.format(app_path=app_path)
instr_directory = '{app_path}/_instrs/'.format(app_path=app_path)
task_directory = '{app_path}/_task'.format(app_path=app_path)
if not os.path.exists(env_directory) : os.makedirs(env_directory)
if not os.path.exists(instr_directory) : os.makedirs(instr_directory)
if not os.path.exists(task_directory) : os.makedirs(task_directory)

# requests/ HTTP
dl_accepted_codes = [200, 201, 202, 203, 204]
