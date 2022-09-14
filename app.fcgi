#!/var/www/localhost/htdocs/.venv/bin/python

from flup.server.fcgi import WSGIServer
from app import appweb

class ScriptNameStripper(object):
   def __init__(self, appweb):
       self.appweb = appweb

   def __call__(self, environ, start_response):
       environ['SCRIPT_NAME'] = ''
       return self.appweb(environ, start_response)

appweb = ScriptNameStripper(appweb)

if __name__ == '__main__':
    WSGIServer(appweb).run()
