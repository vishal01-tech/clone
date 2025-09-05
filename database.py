from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base


# connection to mysql database
engine = create_engine("mysql+pymysql://root:root@localhost/usersdatabase",echo=False)

# declare the base class
Base = declarative_base()

# session to interact with database
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)
