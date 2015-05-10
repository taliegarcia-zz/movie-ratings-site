"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Display the homepage."""

    return render_template("homepage.html")

@app.route('/register')
def registration():
    """Display registration form for new users"""

    return render_template("register.html")

@app.route('/register', methods=["POST"])
def register_new_user():
    """When reqistration form is submitted (via POST request), 
    add them to our User class as a new instance, and add and commit to 'users' DB """

    input_email = request.form.get('email')
    input_password = request.form.get('password')
    input_age = request.form.get('age')
    input_zipcode = request.form.get('zipcode')

    new_user = User(email=input_email, password=input_password, age=input_age, zipcode=input_zipcode)

    db.session.add(new_user)
    db.session.commit()

    return redirect("/") # upon successful registration, redirect to homepage


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/users/<int:id>")
def get_user_by_id(id):
    """Display user info page by user_id
    """
    user = User.query.get(id)

    return render_template("user.html", user=user)


@app.route('/movies')
def movie_list():
    """Show a list of the movies """

    movies_list = Movie.query.all()
   
    return render_template("movie_list.html", movies_list = movies_list)


@app.route("/movies/<int:id>", methods=["GET", "POST"])
def score_movie(id):
    """When user submits a new score on the movie page,
    handle the POST request, and insert the new score into ratings db, 
    or update the score if it already exists.
    """

    movie = Movie.query.get(id)
    user_id = session.get("logged_in_user_id")
    

    # querying to see if user has rated this movie before
    if user_id:
        user_rating = Rating.query.filter_by(movie_id = movie.movie_id, 
                                            user_id = user_id).first()
    else:
        user_rating = None

    rating_scores = [r.score for r in movie.ratings]
    avg_rating = float(sum(rating_scores)) / len(rating_scores)

    prediction = None # initializing prediction variable


    # Prediction code: only predict if the user hasn't rated it.

    if (not user_rating) and user_id: 
        # if user_rating is None AND they are logged in
        user = User.query.get(user_id)
        # get the user object by user_id

        if user:
            # if the user is found in our db, call the predict_rating method on it
            prediction = user.predict_rating(movie)


    # Insert New Score code: only run if user POST's a new score
    # if a rating exists, we can replace it with the new_score by just changing the object attribute
    if request.method == "POST":
        new_score = request.form.get("score")
    
        if user_rating:
            user_rating.score = new_score

        # otherwise, we need to insert the score as a new rating instance
        else:
            new_rating_to_insert = Rating(movie_id=movie_object.movie_id, user_id=user_id, score=new_score)  
            db.session.add(new_rating_to_insert)
            db.session.commit()
    
    return render_template("movie.html", 
                        movie_object=movie, 
                        user_rating=user_rating, 
                        average=avg_rating,
                        prediction=prediction)


@app.route("/login")
def show_login():
    """Show login form."""

    return render_template("login.html")



@app.route("/login", methods=["POST"])
def process_login():
    """Log user into site.
    Compare input email and password to the email and password
    in the 'users' db for authentification.
    """

    input_email = request.form.get('email')
    input_password = request.form.get('password')

    userq = User.query # create query object on User class

    user = userq.filter_by(email=input_email).first() # pull instance of this particular user from User class

    if user: # if there is a returned value for this user
        
        if input_password == user.password: 
            session['logged_in_user_id'] = user.user_id # adding user to the session

            flash('Login successful')
            return redirect('/')

        else:
            flash('Incorrect password')
            return redirect('/login')

    else: 
        flash('No such email')
        return redirect('/login')

@app.route("/logout")
def logout():
    """Logout user"""

    del session['logged_in_user_id']

    flash("You have been logged out.")

    return redirect('/')
    


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()


