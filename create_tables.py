import os
#import sql related libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

#connect to db
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    db.execute("CREATE TABLE IF NOT EXISTS books (id SERIAL NOT NULL, isnb text NOT NULL, title text NOT NULL, author text NOT NULL, year text)")
    print('Table books has been created')

    db.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL NOT NULL, username text UNIQUE NOT NULL, name text NOT NULL, password text NOT NULL)")
    print('Table users has been created')
    db.commit()

if __name__ == "__main__":
    main()