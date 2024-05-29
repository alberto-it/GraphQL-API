## Flask-based GraphQL API for Managing Movies and Genres

### Models

* **models.py:** Defines the Movie and Genre models using SQLAlchemy.
    * Movie: Represents a movie with attributes id, title, year, and a many-to-many relationship with Genre through the movie_genre association table.
    * Genre: Represents a genre with attributes id and name.

### GraphQL Schema

* **schema.py:** Defines the GraphQL schema including queries and mutations for interacting with movies and genres.

### API Endpoint

* **/graphql:** The GraphQL endpoint for querying and mutating data (can cccess the GraphQL API using GraphiQL at http://localhost:5000/graphql)
