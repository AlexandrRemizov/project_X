from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://postgres:1@172.17.0.2/postgres",
                       echo=True,
                       )
engine.connect()
print(engine)   