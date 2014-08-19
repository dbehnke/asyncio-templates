import tornado.web

from tornado.platform.asyncio import AsyncIOMainLoop
import asyncio
import logging

from concurrent.futures import ThreadPoolExecutor
thread_pool = ThreadPoolExecutor(max_workers=20)

#initialize test database
from sa import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

#sqlite memory (broken - has issues with table created in another thread)
#from sqlalchemy.pool import StaticPool
#db_engine = create_engine('sqlite:///:memory:', echo=False,
#                          connect_args={'check_same_thread': False},
#                          poolclass=StaticPool)

#sqlite - file based (kinda broken - works as long as not too much concurrency)
#db_engine = create_engine('sqlite:///test.db', echo=False)

#oracle
#requires cx_Oracle module
from sqlalchemy.pool import QueuePool

#for oracle uncomment either SID or Service connect_string
#SID based
'''
connect_string = """oracle+cx_oracle://user:pass@
            (DESCRIPTION = (ADDRESS = (PROTOCOL = TCP)
            (HOST = hostname)(PORT = 1521))
            (CONNECT_DATA = (SERVER = DEDICATED) (SID = sidhere)))"""
'''
#Service based
connect_string = """oracle+cx_oracle://test:testing@
            (DESCRIPTION = (ADDRESS = (PROTOCOL = TCP)
            (HOST = onyx)(PORT = 1521))
            (CONNECT_DATA = (SERVER = DEDICATED) (SERVICE_NAME = pdb)))"""

db_engine = create_engine(connect_string,
                          poolclass=QueuePool,
                          pool_size=10,
                          pool_recycle=300,
                          echo=True)

#postgres
#requires the psycopg2 module
#from sqlalchemy.pool import QueuePool
#db_engine = create_engine('postgresql://test:testing@localhost/test',
#                          poolclass=QueuePool,
#                          pool_size=10,
#                          pool_recycle=300,
#                          echo=True)


DBSession = scoped_session(
    sessionmaker(
        autoflush=True,
        autocommit=False,
        bind=db_engine
    )
)

base = models.Base
base.metadata.create_all(db_engine)


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


def dbtest():
    session = DBSession()
    try:
        h = models.Hash()
        h.k = 'Hello'
        h.v = 'World'
        session.add(h)
        session.commit()
        session.refresh(h)
        session.close()
        return h
    finally:
        DBSession.remove()


class MainHandler(tornado.web.RequestHandler):
    @coroutine
    def get(self):
        loop = asyncio.get_event_loop()
        h = yield from loop.run_in_executor(thread_pool, dbtest)
        self.write(str(h.id).encode())


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