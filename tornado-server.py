# import tornado.ioloop
import tornado.web

from tornado.platform.asyncio import AsyncIOMainLoop
import asyncio
import logging


# idea from https://gist.github.com/BeholdMyGlory/11067131
def coroutine(func):
    func = asyncio.coroutine(func)
    def decorator(*args, **kwargs):
        future = tornado.concurrent.Future()
        def future_done(f):
            try:
                future.set_result(f.result())
            except Exception as e:
                future.set_exception(e)
        asyncio.async(func(*args, **kwargs)).add_done_callback(future_done)
        return future
    return decorator


# idea from https://gist.github.com/BeholdMyGlory/11067131
def future_wrapper(f):
    future = asyncio.Future()

    def handle_future(ff):
        try:
            future.set_result(ff.result())
        except Exception as e:
            future.set_exception(e)

    tornado.ioloop.IOLoop.current().add_future(f, handle_future)
    return future


class MainHandler(tornado.web.RequestHandler):
    @coroutine
    def get(self):
        yield from asyncio.sleep(2)
        self.write("Hello, world")


app = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == '__main__':
    log = logging.getLogger("")
    formatter = logging.Formatter("%(asctime)s %(levelname)s " +
                                  "[%(module)s:%(lineno)d] %(message)s")
    # setup console logging
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(formatter)
    log.addHandler(ch)
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    app.listen(2302)
    asyncio.get_event_loop().run_forever()


#if __name__ == "__main__":
#    app.listen(2302)
#    AsyncIOMainLoop().install()
#    asyncio.get_event_loop().run_forever()