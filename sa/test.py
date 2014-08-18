def test_database():
    from sa import models
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker()
    engine = create_engine('sqlite:///:memory:', echo=True)
    Session.configure(bind=engine)
    base = models.Base
    base.metadata.create_all(engine)


def test_hash():
    from sa import models
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker()
    engine = create_engine('sqlite:///:memory:', echo=True)
    Session.configure(bind=engine)
    base = models.Base
    base.metadata.create_all(engine)
    session = Session()
    h = models.Hash()
    h.k = 'Hello'
    h.v = 'World'
    session.add(h)
    session.commit()
    print(h)
    assert h.id == 1