from sqlalchemy import create_engine, text, MetaData, \
    Table, Column, Integer, String, ForeignKey, insert
from sqlalchemy.orm import declarative_base, relationship

engine = create_engine("postgresql+psycopg2://postgres:1@172.17.0.2/postgres",
                       echo=True,
                       )
user_table = Table(
    "user_account",
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('name', String(30)),
    Column('password', String)
)
address_table = Table(
    "address",
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('user_id', ForeignKey('user_account.id'), nullable=False),
    Column('email_address', String, nullable=False)
)
Base = declarative_base()


class User(Base):
    __tablename__ = 'user_account'

    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    password = Column(String)

    addresses = relationship("Address", back_populates='user')

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, password={self.password})"


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_kay=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user_account.id'))

    user = relationship("User", back_populates='addresses')

    def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM user_account"))
    print(result)

# metadata_obj.create_all(engine)
