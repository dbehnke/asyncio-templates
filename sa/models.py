from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from sqlalchemy import Column, Integer, String, Sequence


class Hash(Base):
    __tablename__ = 'hash'

    #id = Column(Integer, primary_key=True)
    #for oracle
    id = Column('id', Integer, Sequence('id_seq'), primary_key=True)
    k = Column(String(200))
    v = Column(String(200))

    def __repr__(self):
        return "<Hash(id=%d, k='%s', v='%s')>" % (
                                 self.id, self.k, self.v)