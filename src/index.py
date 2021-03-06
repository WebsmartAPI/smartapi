""" SmartAPI Entry Point """

from threading import Thread

from aiocron import crontab
from biothings.web.index_base import main
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler

from admin import routine
from utils.indices import setup


def run_routine():
    thread = Thread(target=routine, daemon=True)
    thread.start()


class WebAppHandler(RequestHandler):
    def get(self):
        self.render('../web-app/dist/index.html')


if __name__ == '__main__':

    crontab('0 0 * * *', func=run_routine, start=True)
    IOLoop.current().add_callback(setup)
    main([
        (r"/user/?", "handlers.UserInfoHandler"),
        (r"/login/?", "handlers.LoginHandler"),
        (r"/oauth", "handlers.GithubLoginHandler"),
        (r"/logout/?", "handlers.LogoutHandler"),
        (r'/sitemap.xml()', "tornado.web.StaticFileHandler", {'path': '../web-app/dist/sitemap.xml'}),
        (r"/((?:img|css|js|fonts)/.*)", "tornado.web.StaticFileHandler", {
            "path": "../web-app/dist/"
        })], {
        "default_handler_class": WebAppHandler,
        "static_path": "../web-app/dist/",
    }, use_curl=True)
