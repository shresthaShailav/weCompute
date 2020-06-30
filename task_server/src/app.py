import os
import sys
import re
from pprint import pprint
import json
from flask import Flask, url_for, jsonify, request, redirect, abort, send_file
import copy

from utils import Tracker, TaskQueue

app = Flask(__name__)


# configuration parameters 
ENV_DIRECTORY = '{app_path}/environments/'.format(app_path=os.getcwd())
if not os.path.exists(ENV_DIRECTORY) :
    os.makedirs(ENV_DIRECTORY)

INSTR_DIRECTORY = '{app_path}/instructions/'.format(app_path=os.getcwd())
if not os.path.exists(INSTR_DIRECTORY) : 
    os.makedirs(INSTR_DIRECTORY)


@app.route('/')
def index() :
    return 'WeCompute Interface'


""" 
for dev purposes, clear the peer list
"""
@app.route('/clear', methods=['POST'])
def clear() : 
    # empty the active peer list
    Tracker.clear_all_clients()
    msg = {'status' : 'success'}
    return jsonify(msg)



"""
endpoint for checking active peers
"""
@app.route('/peers', methods=['GET', 'POST'])
def peers() : 
    # check the available peers visible
    # improvement : create mechanism so that only peers who approve can be seen

    if request.method == 'GET' : 
        try : 
            # get requests parameters 
            req = {k:v for k,v in dict(request.args).items()}
            if all([isinstance(v, list) for k, v in req.items()]) : 
                req = {k:v[0] for k,v in dict(request.args).items()}  

            # validate request parameters(skipped)
            # authentication/ authorization

            # return active peers visible to requesting client 
            active_peers = Tracker.get_active_clients()
            try : active_peers.remove(req['id'])      # removing requesting client from the list
            except : pass

            msg = {
                'status' : 'success',
                'count' : len(active_peers),
                'peers' : active_peers
                }
        except Exception as e : 
            msg = {
                'status' : 'failure',
                'error' : '{}:{}'.format(e.__class__.__name__, str(e))
                }
        return jsonify(msg)

    if request.method == 'POST'  : 
        try : 
            # get json parameters
            req = request.get_json()
            if req is None : 
                raise Exception('No json found')

            # validate request parameters(skilled) 
            # authentication/ authorization

            # add client to active peers
            # later, you should allow clients to choose who they are visible to
            Tracker.add_active_clients([req['id']])
            msg = { 'status' : 'success'}
        except Exception as e : 
            msg = {
                    'status' : 'failure',
                    'error' : '{}:{}'.format(e.__class__.__name__, str(e))
                }
        return jsonify(msg)


    return "Invalid Request"

""" 
endpoint for task exchange
"""
@app.route('/task', methods=['GET', 'POST'])
def task() : 
    if request.method == 'GET' : 
        try : 
            # get request parameters
            req = {k:v for k,v in dict(request.args).items()}
            if all([isinstance(v, list) for k, v in req.items()]) : 
                req = {k:v[0] for k,v in dict(request.args).items()}  

            # validate request parameters(skipped)
            # authentication/ authorization

            # mark the client as active(Not doing that here anymore) remove soon
            #Tracker.add_active_clients([req['id']])

            # process request
            task = TaskQueue.pop(req['id'])
            if task : 
                msg = {
                    'tasks' : [task],
                    'count' : 1,
                    'status' : 'success'
                    }
            else : 
                msg = {
                    'count' : 0,
                    'status' : 'success'
                    }
        except Exception as e : 
            msg = {
                    'status' : 'failure',
                    'error' : '{}:{}'.format(e.__class__.__name__, str(e))
                }
        return jsonify(msg)


    if request.method == 'POST' : 
        try : 
            # get json parameters
            req = request.get_json()
            if req is None : 
                raise Exception('No json found')

            # validate request parameters(skilled) 
            # authentication/ authorization

            # process request
            task = copy.deepcopy(req)
            TaskQueue.push(req['target_id'], task)
            msg = { 'status' : 'success'}
        except Exception as e : 
            msg = {
                    'status' : 'failure',
                    'error' : '{}:{}'.format(e.__class__.__name__, str(e))
                    }
        return jsonify(msg)


"""
endpoint for environment file upload download
"""
@app.route('/env/<string:key>', methods=['GET'])
def get_env_file(key) : 
    """
        Download/Upload a file based on key to environments folder
        For now, nothing fancy, the key is the filename to a dockerfile
    """
    #return str(key)
    if request.method == 'GET' : 
        file_path = '{ENV_DIR}/{key}'.format(ENV_DIR=ENV_DIRECTORY, key=key)
        if os.path.exists(file_path) : 
            return send_file(file_path, mimetype='application/zip')
        else :
            return "not found", 400


@app.route('/env', methods=['POST'])
def put_env_file() : 
    if request.method == 'POST' : 

        key = request.headers.get('key')
        if '/' in key:
            abort(400, "no subdirectories allowed")

        # todo : check for conflict

        with open(os.path.join(ENV_DIRECTORY, key), "wb") as f : 
            f.write(request.data)

        # created
        return "success",201


if __name__ == "__main__" : 
    app.run(host="0.0.0.0", debug=True)
