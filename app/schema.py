import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.models import Movie as MovieModel, db
from app.models import Genre as GenreModel

from sqlalchemy.orm import Session

class Movie(SQLAlchemyObjectType):
    class Meta: model = MovieModel

class Genre(SQLAlchemyObjectType):
    class Meta:
        model = GenreModel

class Query(graphene.ObjectType):
    movies = graphene.List(Movie)
    search_movies = graphene.List(Movie, title=graphene.String(), year=graphene.Int())

    def resolve_movies(root, info): return db.session.execute(db.select(MovieModel)).scalars()

    def resolve_search_movies(root, info, title=None, year=None):        
        query = db.select(MovieModel)
        if title:    query = query.where(MovieModel.title.ilike(f'%{title}%'))
        if year:     query = query.where(MovieModel.year == year)
        return db.session.execute(query).scalars().all()

    movies_by_genre = graphene.List(Movie, genre_id=graphene.NonNull(graphene.Int))

    def resolve_movies_by_genre(root, info, genre_id):
        query = db.session.query(MovieModel) \
            .join(GenreModel, MovieModel.genres) \
            .filter(GenreModel.id == genre_id)
        return query.all()
    
    genre_by_movie = graphene.List(Genre, movie_id=graphene.NonNull(graphene.Int))

    def resolve_genre_by_movie(root, info, movie_id):
        query = db.session.query(GenreModel) \
            .join(MovieModel, GenreModel.movies) \
            .filter(MovieModel.id == movie_id)
        return query.all() 

class AddMovie(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        year = graphene.Int(required=True)
        genre_ids = graphene.List(graphene.NonNull(graphene.Int))  # List of required Genre IDs

    movie = graphene.Field(Movie)

    def mutate(root, info, title, year, genre_ids):
        with Session(db.engine) as session: 
            with session.begin():
                movie = MovieModel(title=title, year=year)
                movie.genres = [session.query(GenreModel).get(genre_id) for genre_id in genre_ids]
                session.add(movie)
            
            session.refresh(movie)
            return AddMovie(movie=movie)

class UpdateMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        year = graphene.Int()

    movie = graphene.Field(Movie)

    def mutate(root, info, id, title=None, year=None):
        movie = db.session.get(MovieModel, id)         
        if not movie: return None
        if title: movie.title = title
        if year:  movie.year = year
        db.session.commit()
        return UpdateMovie(movie=movie)

class DeleteMovie(graphene.Mutation):
    class Arguments: id = graphene.Int(required=True)

    message = graphene.String()

    def mutate(root, info, id):
        movie = db.session.get(MovieModel, id)         
        if not movie: return DeleteMovie(message="That movie does not exist")
        else:
            db.session.delete(movie)
            db.session.commit()
            return DeleteMovie(message="Success")
        
class Genre(SQLAlchemyObjectType):
    class Meta: model = GenreModel

class CreateGenre(graphene.Mutation):
    class Arguments: name = graphene.String(required=True)

    genre = graphene.Field(Genre)

    def mutate(self, info, name):
        with Session(db.engine) as session: 
            with session.begin():
                genre = GenreModel(name=name)
                session.add(genre)
            
            session.refresh(genre)
            return CreateGenre(genre=genre)
        
class UpdateGenre(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)

    genre = graphene.Field(Genre)

    def mutate(self, info, id, name=None):
        genre = db.session.query(GenreModel).get(id)         
        if not genre: return None
        if name: genre.name = name
        db.session.commit()
        return UpdateGenre(genre=genre)

class DeleteGenre(graphene.Mutation):
    class Arguments: id = graphene.Int(required=True)

    message = graphene.String()

    def mutate(self, info, id):
        genre = db.session.query(GenreModel).get(id)         
        if not genre: return DeleteGenre(message="That genre does not exist")
        else:
            db.session.delete(genre)
            db.session.commit()
            return DeleteGenre(message="Genre deleted successfully")

class Mutation(graphene.ObjectType):
    create_movie = AddMovie.Field()
    update_movie = UpdateMovie.Field()
    delete_movie = DeleteMovie.Field()

    create_genre = CreateGenre.Field()
    update_genre = UpdateGenre.Field()
    delete_genre = DeleteGenre.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)