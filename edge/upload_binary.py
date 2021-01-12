import gateway.link


http_upload_binary = gateway.link.Replicate(
    channels = {140, 160, 180, 600, 10002},
    start_delay = 0, 
    transmit_rate = 1, 
    host_api_url = '/host/',
    max_connect_attempts = 50, 
    config_filepath = '/home/heta/Z/app/python/dogger/', 
    config_filename = 'conf.ini')

http_upload_binary.run()
