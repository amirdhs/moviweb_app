from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User, Movie
from datamanager.sqlite_data_manager import SQLiteDataManager
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviweb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'
db.init_app(app)

data_manager = SQLiteDataManager()
OMDB_API_KEY = 'd5776c1'

# Fetch movie data from OMDb API
def fetch_movie_data(movie_title):
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={movie_title}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("Response") == "True":
            return {
                "title": data.get("Title"),
                "director": data.get("Director"),
                "year": int(data.get("Year", 0)),
                "rating": float(data.get("imdbRating", 0)),
            }
    return None

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# List all users
@app.route('/users')
def list_users():
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)

# List movies for a specific user
@app.route('/users/<int:user_id>')
def user_movies(user_id):
    movies = data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', movies=movies, user_id=user_id)

# Add a new user
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        data_manager.add_user(name)
        flash('User added successfully!', 'success')
        return redirect(url_for('list_users'))
    return render_template('add_user.html')

# Add a new movie for a user
@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == 'POST':
        movie_title = request.form['title']
        movie_data = fetch_movie_data(movie_title)
        if movie_data:
            data_manager.add_movie(user_id, **movie_data)
            flash('Movie added successfully!', 'success')
        else:
            flash('Movie not found!', 'error')
        return redirect(url_for('user_movies', user_id=user_id))
    return render_template('add_movie.html', user_id=user_id)

# Update a movie
@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    movie = Movie.query.get(movie_id)
    if request.method == 'POST':
        title = request.form['title']
        director = request.form['director']
        year = request.form['year']
        rating = request.form['rating']
        data_manager.update_movie(movie_id, title, director, year, rating)
        flash('Movie updated successfully!', 'success')
        return redirect(url_for('user_movies', user_id=user_id))
    return render_template('update_movie.html', movie=movie, user_id=user_id)

# Delete a movie
@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>')
def delete_movie(user_id, movie_id):
    data_manager.delete_movie(movie_id)
    flash('Movie deleted successfully!', 'success')
    return redirect(url_for('user_movies', user_id=user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)