from abc import ABC, abstractmethod


class DataManagerInterface(ABC):
    """
    Interface for data manager classes to implement.
    Enforces a common API for all data manager implementations.
    """

    @abstractmethod
    def get_all_users(self):
        """
        Returns a list of all users.

        Returns:
            list: A list of user dictionaries with 'id' and 'name' keys.
        """
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """
        Returns a list of movies for a specific user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list: A list of movie dictionaries with 'id', 'name', 'director',
                  'year', 'rating', and 'user_id' keys.
        """
        pass

    @abstractmethod
    def add_user(self, name):
        """
        Adds a new user to the database.

        Args:
            name (str): The name of the user.

        Returns:
            int: The ID of the newly created user.
        """
        pass

    @abstractmethod
    def add_movie(self, user_id, movie_data):
        """
        Adds a new movie to a user's list.

        Args:
            user_id (int): The ID of the user.
            movie_data (dict): A dictionary containing the movie data.

        Returns:
            int: The ID of the newly created movie.
        """
        pass

    @abstractmethod
    def update_movie(self, movie_id, movie_data):
        """
        Updates a movie in the database.

        Args:
            movie_id (int): The ID of the movie.
            movie_data (dict): A dictionary containing the updated movie data.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        """
        Deletes a movie from the database.

        Args:
            movie_id (int): The ID of the movie.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        pass

    @abstractmethod
    def get_movie(self, movie_id):
        """
        Gets a specific movie from the database.

        Args:
            movie_id (int): The ID of the movie.

        Returns:
            dict: A dictionary containing the movie data.
        """
        pass

    @abstractmethod
    def get_user(self, user_id):
        """
        Gets a specific user from the database.

        Args:
            user_id (int): The ID of the user.

        Returns:
            dict: A dictionary containing the user data.
        """
        pass