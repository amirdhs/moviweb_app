import sqlite3
import os
import requests
from datamanager.data_manager_interface import DataManagerInterface


class SQLiteDataManager(DataManagerInterface):
    """
    SQLite implementation of the DataManagerInterface.
    Manages database operations for the MoviWeb application.
    """

    def __init__(self, db_file_name):
        """
        Initialize the SQLite data manager.

        Args:
            db_file_name (str): The name of the SQLite database file.
        """
        self.db_file_name = db_file_name

        # Create the database directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_file_name), exist_ok=True)

        # Create the tables if they don't exist
        self._create_tables()

    def _create_tables(self):
        """Create the necessary tables if they don't exist."""
        conn = sqlite3.connect(self.db_file_name)
        cursor = conn.cursor()

        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        ''')

        # Create movies table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            director TEXT NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            user_id INTEGER NOT NULL,
            poster_url TEXT,  
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        ''')

        conn.commit()
        conn.close()

    def get_all_users(self):
        """
        Returns a list of all users.

        Returns:
            list: A list of user dictionaries with 'id' and 'name' keys.
        """
        conn = sqlite3.connect(self.db_file_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT id, name FROM users')
        users = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return users

    def add_user(self, name):
        """
        Adds a new user to the database.

        Args:
            name (str): The name of the user.

        Returns:
            int: The ID of the newly created user.
        """
        conn = sqlite3.connect(self.db_file_name)
        cursor = conn.cursor()

        cursor.execute('INSERT INTO users (name) VALUES (?)', (name,))
        user_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return user_id

    def add_movie(self, user_id, movie_data):
        # Fetch movie details from OMDB API if only title is provided
        if 'name' in movie_data and not all(key in movie_data for key in ['director', 'year', 'rating', 'poster_url']):
            try:
                omdb_api_key = os.environ.get('OMDB_API_KEY', 'placeholder_key')
                response = requests.get(
                    f"http://www.omdbapi.com/?t={movie_data['name']}&apikey={omdb_api_key}"
                )
                omdb_data = response.json()

                if omdb_data.get('Response') == 'True':
                    movie_data['name'] = omdb_data.get('Title', 'Unknown')
                    movie_data['director'] = omdb_data.get('Director', 'Unknown')
                    movie_data['year'] = int(omdb_data.get('Year', '0').split('–')[0])
                    movie_data['rating'] = float(omdb_data.get('imdbRating', '0'))
                    movie_data['poster_url'] = omdb_data.get('Poster', '')
            except Exception as e:
                print(f"Error fetching movie data: {e}")

        conn = sqlite3.connect(self.db_file_name)
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO movies (name, director, year, rating, user_id, poster_url)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            movie_data.get('name', 'Unknown'),
            movie_data.get('director', 'Unknown'),
            movie_data.get('year', 0),
            movie_data.get('rating', 0.0),
            user_id,
            movie_data.get('poster_url', '')
        ))

        movie_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return movie_id

    def update_movie(self, movie_id, movie_data):
        """
        Updates a movie in the database.

        Args:
            movie_id (int): The ID of the movie.
            movie_data (dict): A dictionary containing the updated movie data.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        conn = sqlite3.connect(self.db_file_name)
        cursor = conn.cursor()

        cursor.execute('''
        UPDATE movies
        SET name = ?, director = ?, year = ?, rating = ?
        WHERE id = ?
        ''', (
            movie_data.get('name', 'Unknown'),
            movie_data.get('director', 'Unknown'),
            movie_data.get('year', 0),
            movie_data.get('rating', 0.0),
            movie_id
        ))

        success = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return success

    def delete_movie(self, movie_id):
        """
        Deletes a movie from the database.

        Args:
            movie_id (int): The ID of the movie.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        conn = sqlite3.connect(self.db_file_name)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
        success = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return success

    def get_user_movies(self, user_id):
        """
        Returns a list of movies for a specific user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list: A list of movie dictionaries.
        """
        conn = sqlite3.connect(self.db_file_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
        SELECT id, name, director, year, rating, user_id, poster_url
        FROM movies 
        WHERE user_id = ?
        ORDER BY name
        ''', (user_id,))

        movies = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return movies

    def get_movie(self, movie_id):
        """
        Gets a specific movie from the database.

        Args:
            movie_id (int): The ID of the movie.

        Returns:
            dict: A dictionary containing the movie data.
        """
        conn = sqlite3.connect(self.db_file_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
        SELECT id, name, director, year, rating, user_id, poster_url
        FROM movies 
        WHERE id = ?
        ''', (movie_id,))

        row = cursor.fetchone()
        movie = dict(row) if row else None

        conn.close()
        return movie

    def get_user(self, user_id):
        """
        Gets a specific user from the database.

        Args:
            user_id (int): The ID of the user.

        Returns:
            dict: A dictionary containing the user data.
        """
        conn = sqlite3.connect(self.db_file_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT id, name FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        user = dict(row) if row else None

        conn.close()
        return user