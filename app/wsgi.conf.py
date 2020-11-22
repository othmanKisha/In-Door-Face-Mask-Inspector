bind = '0.0.0.0:5000'
workers = 1
threads = 9
worker_class = 'egg:meinheld#gunicorn_worker'
timeout = 120
capture_output = True