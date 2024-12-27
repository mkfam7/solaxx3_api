from os import environ

wsgi_app = "my_api.wsgi:application"
workers = 3
bind = environ.get("REST_API_ADDRESS", "127.0.0.1:8000")

accesslog = "-"
access_log_format = '"%(r)s" %(s)s %(b)s'
errorlog = "-"
