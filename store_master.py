import gateway.store

numpy_sql = gateway.store.NumpyFile(channels = {21,23,20,24,22,161,162,163,164}, config_filepath = '/home/heta/Z/app/python/dogger/', config_filename = 'conf.ini')
numpy_sql.run()
