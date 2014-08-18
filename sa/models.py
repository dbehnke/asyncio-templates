from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from sqlalchemy import Column, Integer, String


class Hash(Base):
    __tablename__ = 'hash'

    id = Column(Integer, primary_key=True)
    k = Column(String)
    v = Column(String)

    def __repr__(self):
        return "<Hash(id=%d, k='%s', v='%s')>" % (
                                 self.id, self.k, self.v)