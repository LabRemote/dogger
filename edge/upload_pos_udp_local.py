import gateway.uplink


udp_upload_pos_local = gateway.uplink.UdpNmeaPos(
    channels = {61011,61012}, 
    start_delay = 0,
    port = 4444,
    nmea_prepend = 'GPGLL,',
    nmea_append = ',A',
    max_age = 10,
    config_filepath = '/home/heta/Z/app/python/dogger/', 
    config_filename = 'conf_udp_local.ini')

udp_upload_pos_local.run()
