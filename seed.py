"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from model import User, Rating, Movie, connect_to_db, db
from server import app
import datetime


def load_users():
    """Load users from u.user into database."""
    open_file = open("./seed_data/u.user")
    
    for line in open_file:
        # user_info = line.readline() # creates string of each line, with ending \n character
        user_info = line.rstrip().split("|") # creates a list of the items on the line
        user_id, age, zipcode = user_info[0], user_info[1], user_info[-1]
        new_user = User(user_id=user_id, 
                        email="NULL", 
                        password="NULL", 
                        age=age, 
                        zipcode=zipcode)
        

        db.session.add(new_user)

    db.session.commit()



def load_movies():
    """Load movies from u.item into database."""
    open_file =open("./seed_data/u.item")

    for line in open_file:
        # user_info = line.readline() # creates string of each line, with ending \n character
        movie_info = line.rstrip().split("|")[:5] # creates a list of the items on the line
        
        movie_id, title, date_old, junk, imdb_url = movie_info
        
        title = title[:-7]
        title = title.decode("latin-1")
        
        if date_old:
            released_at = datetime.datetime.strptime(date_old, "%d-%b-%Y")
              
        else:
            released_at = None

        movie = Movie(movie_id=movie_id, 
                    title=title, 
                    released_at=released_at, 
                    imdb_url=imdb_url)
        
        db.session.add(movie)

    db.session.commit()

def load_ratings():
    """Load ratings from u.data into database."""
    open_file = open("./seed_data/u.data")
    
    for line in open_file:
        # user_info = line.readline() # creates string of each line, with ending \n character
        rating_info = line.rstrip().split("\t") # creates a list of the items on the line
        user_id, movie_id, score = rating_info[0], rating_info[1], rating_info[2]
        new_rating = Rating(user_id=user_id, 
                            movie_id=movie_id, 
                            score=score)
        

        db.session.add(new_rating)


    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()
    load_users()
    load_movies()
    load_ratings()
