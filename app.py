import os
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from datamanager.sqlite_data_manager import SQLiteDataManager
import requests
from dotenv import load_dotenv
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
app.config['OMDB_API_KEY'] = os.environ.get('OMDB_API_KEY', 'placeholder_key')

# Create data manager
db_path = os.path.join(app.instance_path, 'moviwebapp.db')
data_manager = SQLiteDataManager(db_path)


# Home route
@app.route('/')
def home():
    featured_movies = [
        {
            'name': 'Inception',
            'director': 'Christopher Nolan',
            'year': 2010,
            'rating': 8.8,
            'poster_url': 'https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg'
        },
        {
            'name': 'The Dark Knight',
            'director': 'Christopher Nolan',
            'year': 2008,
            'rating': 9.0,
            'poster_url': 'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg'
        },
        {
            'name': 'Interstellar',
            'director': 'Christopher Nolan',
            'year': 2014,
            'rating': 8.6,
            'poster_url': 'https://m.media-amazon.com/images/M/MV5BYzdjMDAxZGItMjI2My00ODA1LTlkNzItOWFjMDU5ZDJlYWY3XkEyXkFqcGc@._V1_SX300.jpg'
        }
    ]
    return render_template('home.html', featured_movies=featured_movies)


# Users list route
@app.route('/users')
def list_users():
    """Display a list of all users."""
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


# User movies route
@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """Display a user's favorite movies."""
    user = data_manager.get_user(user_id)
    if not user:
        abort(404)

    movies = data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', user=user, movies=movies)


# Add user route
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Display and process the add user form."""
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('User name is required!', 'error')
        else:
            user_id = data_manager.add_user(name)
            flash(f'User {name} added successfully!', 'success')
            return redirect(url_for('user_movies', user_id=user_id))

    return render_template('add_user.html')

@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    user = data_manager.get_user(user_id)
    if not user:
        abort(404)

    if request.method == 'POST':
        movie_data = {
            'name': request.form.get('name'),
            'director': request.form.get('director'),
            'year': request.form.get('year'),
            'rating': request.form.get('rating'),
            'poster_url': request.form.get('poster_url', '')
        }

        # Fetch movie details from OMDB API if only title is provided
        if movie_data['name'] and not all([movie_data.get('director'), movie_data.get('year'), movie_data.get('rating')]):
            try:
                response = requests.get(
                    f"http://www.omdbapi.com/?t={movie_data['name']}&apikey={app.config['OMDB_API_KEY']}"
                )
                omdb_data = response.json()

                if omdb_data.get('Response') == 'True':
                    movie_data['director'] = omdb_data.get('Director', 'Unknown')
                    movie_data['year'] = int(omdb_data.get('Year', '0').split('–')[0])
                    movie_data['rating'] = float(omdb_data.get('imdbRating', '0'))
                    movie_data['poster_url'] = omdb_data.get('Poster', '')
                else:
                    flash('Movie not found in OMDB database!', 'error')
            except Exception as e:
                flash(f'Error fetching movie data: {e}', 'error')

        if not movie_data['name']:
            flash('Movie name is required!', 'error')
        else:
            try:
                if movie_data['year']:
                    movie_data['year'] = int(movie_data['year'])
                if movie_data['rating']:
                    movie_data['rating'] = float(movie_data['rating'])

                data_manager.add_movie(user_id, movie_data)
                flash(f'Movie {movie_data["name"]} added successfully!', 'success')
                return redirect(url_for('user_movies', user_id=user_id))
            except ValueError:
                flash('Invalid year or rating! Please enter numeric values.', 'error')
                return redirect(url_for('add_movie', user_id=user_id))

    return render_template('add_movie.html', user=user)

# Update movie route
@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    user = data_manager.get_user(user_id)
    if not user:
        abort(404)

    movie = data_manager.get_movie(movie_id)
    if not movie or movie['user_id'] != user_id:
        abort(404)

    if request.method == 'POST':
        movie_data = {
            'name': request.form.get('name'),
            'director': request.form.get('director'),
            'year': request.form.get('year'),
            'rating': request.form.get('rating')
        }

        if not movie_data['name']:
            flash('Movie name is required!', 'error')
        else:
            try:
                if movie_data['year']:
                    movie_data['year'] = int(movie_data['year'])
                if movie_data['rating']:
                    movie_data['rating'] = float(movie_data['rating'])

                data_manager.update_movie(movie_id, movie_data)
                flash(f'Movie {movie_data["name"]} updated successfully!', 'success')
                return redirect(url_for('user_movies', user_id=user_id))
            except ValueError:
                flash('Invalid year or rating!', 'error')

    return render_template('update_movie.html', user=user, movie=movie)

# Delete movie route
@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>')
def delete_movie(user_id, movie_id):
    user = data_manager.get_user(user_id)
    if not user:
        abort(404)

    movie = data_manager.get_movie(movie_id)
    if not movie or movie['user_id'] != user_id:
        abort(404)

    movie_name = movie['name']
    if data_manager.delete_movie(movie_id):
        flash(f'Movie {movie_name} deleted successfully!', 'success')
    else:
        flash(f'Failed to delete movie {movie_name}!', 'error')

    return redirect(url_for('user_movies', user_id=user_id))

@app.route('/search', methods=['GET'])
def search_movies():
    query = request.args.get('query', '').strip()
    if not query:
        flash('Please enter a search term.', 'error')
        return redirect(url_for('home'))

    try:

        response = requests.get(
            f"http://www.omdbapi.com/?s={query}&apikey={app.config['OMDB_API_KEY']}"
        )
        data = response.json()

        if data.get('Response') == 'True':
            movies = data['Search']
        else:
            movies = []
            flash(data.get('Error', 'No movies found.'), 'error')
    except Exception as e:
        flash(f'Error fetching movie data: {e}', 'error')
        movies = []

    return render_template('search_results.html', query=query, movies=movies)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('error.html', error=e, title='Page Not Found',
                           message='The requested page was not found.'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors."""
    return render_template('error.html', error=e, title='Server Error',
                           message='An internal server error occurred.'), 500


# Run the app
if __name__ == '__main__':
    app.run(debug=True)