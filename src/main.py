import time
import requests
from pprint import pprint, pformat
import logging
import docker
import os
import shutil
from zipfile import ZipFile

from util import *

client = docker.from_env()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

import config as cfg

def listen() :
    """ listens to the task server for new tasks """
    last_active_time = 0
    while True : 
        # mark self as active every 5 minutes (so that others can request compute)
        if time.time() - last_active_time > 5 * 60 * 60 : 
            peer_endpoint = '{host}/peers'.format(host=cfg.host)
            json_data = {
                    'id' : cfg.self_id,
                    'visibility' : 'public'
                    }
            try : 
                response = requests.post(peer_endpoint, json=json_data).json()
                if response['status'] == 'success' : 
                    last_active_time = time.time()
                    logger.info("Successfully marked self as active")
                elif response['status'] == 'failure' : 
                    logger.error("Server failed to mark self as active")
                    continue
                else : 
                    raise Exception("Invalid Status")
            except Exception as e : 
                logger.error("Unable to mark self as active. Raised {}:{}".format(e.__class__.__name__, str(e)))
                time.sleep(cfg.wait_interval)
                continue

        
        # query for new task
        endpoint = '{host}/task'.format(host=cfg.host)
        params = {'id': cfg.self_id}

        try :
            response = requests.get(endpoint, params=params).json()
        except Exception as e : 
            logger.error('Unable to fetch task. Raised {}:{}'.format(e.__class__.__name__, str(e)))
            time.sleep(cfg.wait_interval)
            continue

        logger.info("retrieved response : {}".format(pformat(response)))

        if response['status'] == 'failure' : 
            logger.error("Server error. Failed to check for new task")
            time.sleep(cfg.wait_interval)


        if response['status'] == 'success' : 

            if response['count'] == 0 : 
                logger.info("No task to perform")
                time.sleep(cfg.wait_interval)
                continue

            # if task, process all the task appropriately
            for task in response['tasks'] : 
                try : 
                    process_task(task)
                except Exception as e : 
                    error = "Unable to process task. Raised {}:{}".format(e.__class__.__name__, str(e))
                    logger.error(error)


def process_task(task) : 
    # fill task (for any missing keys, set default values)
    task['use_cache'] = task.pop('use_cache', True)

    logger.info("processing task: {}\n".format(pformat(task)))

    # set environment
    
    if int(task['env_code']) == 1 : 
        # excpects an (encrypted) zipped app with dockerfile

        env_file_path = '{env_path}/{requester}-{key}'
        key = task['env_url'].replace('https://','').replace('http://','').replace('www.','').replace('/','_').replace(':','-')
        env_file_path = env_file_path.format(env_path = cfg.env_directory, requester=task['requester_id'], key=key)

        if os.path.exists(env_file_path) : 
            found = True
            logger.info("Found cached env for {}.".format(task['env_url']))
        else : 
            found = False

        if not found or not task['use_cache'] :
            # download env file
            try : 
                env_data = requests.get(task['env_url'])

                if not env_data.status_code in cfg.dl_accepted_codes : 
                    error = 'Unsupported response : {}'.format(env_data.status_code)
                    raise Exception(error)

                with open(env_file_path, 'wb') as f : 
                    f.write(env_data.content)
                logger.info("Successfully downloaded environment file")

            except Exception as e : 
                logger.error("Unable to download from {}. Raised {}:{}".format(task['env_url'], e.__class__.__name__, str(e)))
                return

            # decrypt env file
            try : 
                encryption = task['env_encryption']
                if encryption is None : 
                    logger.info("No encryption mentioned. Decryption skipped.")
                else : 
                    secret = task['env_secret']
                    status = decrypt_file(encryption, secret, env_file_path, env_file_path)
                    if status == False : raise Exception("Decryption of File Failed")
                    logger.info("Successfully Decrypted file")
            except Exception as e : 
                logger.error("Unable to decrypt env file. Raised {}:{}".format(e.__class__.__name__, str(e)))
                if os.path.isfile(env_file_path) : os.remove(env_file_path)
                logger.info("deleted downloaded env file")
                return
        else : 
            logger.info("Skipping Download and Decryption")

        # uncompress and move the contents to task directory
        clear_directory(cfg.task_directory)
        if task['env_compression'] == 'zip' : 
            with ZipFile(env_file_path) as zip_obj :
                zip_obj.extractall(cfg.task_directory)
        else : 
            logger.error("Compression type : {} Not supported".format(task['env_compression']))
            return
        logger.info("Successfully extracted env file content to task_directory")

        # build docker image in task_directory
        try : 
            tag = 'env_{}'.format(os.path.basename(env_file_path)).lower()        # tag must be lowercase
            tag = tag.replace('-','')                                             # causes error sometimes so get rid of those chars
            build_params = {
                    'path' : cfg.task_directory,
                    'tag' : tag
                    }
            client.images.build(**build_params)
            logger.info("Successfully built image {}".format(tag))
        except Exception as e : 
            logger.error("Unable to build image. Raised {}:{}".format(e.__class__.__name__, str(e)))
            return


    # instruction procedure
    if int(task['instr_code']) == 1 : 
        # executes 'instr_cmd' in a detached container

        # start container (volumes unused for now)
        volumes = {}
        container = client.containers.run(tag, volumes=volumes, detach=True)
        logger.info("Initiated container : {}".format(str(container)))

        # execute command 
        command = task['instr_cmd']
        result = container.exec_run(command)
        print(result.output)

        # kill the container 
        container.kill()
        logger.info("Killed container : {}".format(str(container)))

        # return the result output to the queue of the requester 
        endpoint = '{host}/task'.format(host=cfg.host)
        json_data = {
            'requester_id' : cfg.self_id,
            'target_id' : task['requester_id'],
            'task_id' : task['task_id'],
            'env_code' : 0,
            'instr_code': 0,
            'response' : str(result.output)
        }
        headers=None

        try : 
            response = requests.post(endpoint, json=json_data, headers=None).json()
        except Exception as e : 
            logger.info("Failed to return response to requester. Raised {}:{}".format(e.__class__.__name__, str(e)))
            return 
        logger.info("Successfully posted response : {}".format(pformat(json_data)))
   
    return  


if __name__ == '__main__' : 
    listen()
