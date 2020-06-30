def get_environ(var, default) :
    try : 
        val = os.environ[var]
        return val 
    except : 
        return default

redis_endpoint = get_environ('REDIS_ENDPOINT', 'localhost:6379')


