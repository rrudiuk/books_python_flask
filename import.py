#import libraries for svn
import csv
import os
#import libraries for sql
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

#Create env variable that will store db url
engine = create_engine(os.getenv("DATABASE_URL"))
#Session managment
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isnb, title, author, year in reader:
        db.execute("INSERT INTO books (isnb, title, author, year) VALUES (:isnb, :title, :author, :year)",
                    {"isnb": isnb, "title": title, "author": author, "year": year})
        print(f"Added book from {title} written by {author} in {year}.")
    db.commit()

if __name__ == "__main__":
    main()