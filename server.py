"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, jsonify, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    # a = jsonify([1,3])
    # return a
    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/users/<user_id>")
def user_details(user_id):
    """Show user details"""

    user_info = User.query.filter_by(user_id=user_id).first()

    return render_template("user_details.html", user_info=user_info)


@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movie = Movie.query
    movies = movie.order_by("title").all()
    return render_template("movie_list.html", movies=movies)


@app.route("/movies/<movie_id>")
def movie_details(movie_id):
    """Show movie details"""

    movie_info = Movie.query.filter_by(movie_id=movie_id).first()

    return render_template("movie_details.html", movie_info=movie_info)


@app.route("/movierating", methods=["POST"])
def movie_rating():
    """Update or add movie rating to database."""

    rating = request.form.get("rating")
    movie_id = request.form.get("movie_id")
    current_user = session["user_id"]

    existing_rating = Rating.query.filter_by(user_id=current_user, movie_id=movie_id).first()

    if existing_rating is None:
        new_rating = Rating(user_id=current_user, movie_id=movie_id, score=rating)

        db.session.add(new_rating)
        db.session.commit()

        return redirect(request.referrer)

    else:
        existing_rating.score = rating
        db.session.commit()

        return redirect(request.referrer)


@app.route("/register", methods=["GET"])
def register_form():
    """Show registration form."""

    return render_template("registration_form.html")


@app.route("/register", methods=["POST"])
def register_process():
    """Get information from registration form."""

    email = request.form.get("email")
    password = request.form.get("password")
    age = request.form.get("age")
    zipcode = str(request.form.get("zipcode"))

    existing_email = User.query.filter_by(email=email).first()
    # print existing_email

    if existing_email is None:
        new_user = User(email=email, password=password, age=age, zipcode=zipcode)

        db.session.add(new_user)
        db.session.commit()

        return redirect("/")

    else:
        return redirect("/")


@app.route("/login", methods=["POST", "GET"])
def do_login():
    """Attempt to log user in."""

    if request.method == "GET":
        return render_template("login_form.html")

    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        existing_email = User.query.filter_by(email=email).first()

        if existing_email is not None:
            existing_password = existing_email.password
            if existing_password == password:
                # add user to session
                session["user_id"] = existing_email.user_id

                flash("Successfully logged in.")
                return redirect("/")
            else:
                flash("Incorrect password.")
                return redirect('/login')

        else:
            flash("Incorrect email.")
            return redirect('/login')


@app.route("/logout")
def do_logout():
    """Log user out."""

    flash("Goodbye.")
    session["user_id"] = ""

    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)


    app.run(port=5000, host='0.0.0.0')
