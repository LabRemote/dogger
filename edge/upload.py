import gateway.uplink


http_upload = gateway.uplink.Replicate(
    channels = {20,21,23,24,40,97,98,99,100,161,500}, 
    start_delay = 0, 
    host_api_url = '/host/', 
    max_connect_attempts = 50, 
    config_filepath = '/home/heta/Z/app/python/dogger/', 
    config_filename = 'conf.ini')

http_upload.run()
