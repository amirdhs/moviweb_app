from datamanager.data_manager_interface import DataManagerInterface
from models import db, User, Movie

class SQLiteDataManager(DataManagerInterface):
    def get_all_users(self):
        return User.query.all()

    def get_user_movies(self, user_id):
        user = User.query.get(user_id)
        return user.movies if user else []

    def add_user(self, name):
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()

    def add_movie(self, user_id, title, director, year, rating):
        new_movie = Movie(title=title, director=director, year=year, rating=rating, user_id=user_id)
        db.session.add(new_movie)
        db.session.commit()

    def update_movie(self, movie_id, title, director, year, rating):
        movie = Movie.query.get(movie_id)
        if movie:
            movie.title = title
            movie.director = director
            movie.year = year
            movie.rating = rating
            db.session.commit()

    def delete_movie(self, movie_id):
        movie = Movie.query.get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()