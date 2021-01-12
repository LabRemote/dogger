import gateway.link


udp_upload_local = gateway.link.SqlUdpNmeaLines(
    channels = {144,145}, 
    start_delay = 0,
    transmit_rate = 1, 
    port = 4444,
    max_age = 10,
    config_filepath = '/home/heta/Z/app/python/dogger/', 
    config_filename = 'conf_udp_local.ini')

udp_upload_local.run()
