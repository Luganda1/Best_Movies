from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.exc import IntegrityError
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
import requests
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('APP_Secret_Key')
TMDB_API_KEY = os.environ.get('TMDB_Apikey')
TMDB_ACCESS_TOKEN = os.environ.get('TMDB_Access_Token')
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movie1-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
QUERY_MOVIE = ''
MOVIE_ID = None
RATING = 0
REVIEW = 'Edit'



# SQLAlchemy model
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(700), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(260), nullable=False)
    trailer = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'<Movie {self.title}'


db.create_all()
# try:
#     new_movie = Movie(
#         title="Phone Booth",
#         year=2002,
#         description=f"Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's "
#                     f"sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to "
#                     f"a jaw-dropping climax.",
#         rating=7.3,
#         ranking=10,
#         review="My favourite character was the caller.",
#         trailer="https://www.youtube.com/watch?v=",
#         img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#     )
#     db.session.add(new_movie)
#     db.session.commit()
# except IntegrityError:
#     pass


# Edit form class
class AddForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    submit = SubmitField(label='Add Movie')

# Edit form class
class EditForm(FlaskForm):
    rating = StringField(label='Rating', validators=[DataRequired()])
    review = StringField(label='Review', validators=[DataRequired()])
    submit = SubmitField(label='Edit Movie')




@app.route("/")
def home():
    # all_movies = Movie.query.all()
    # all_movies = Movie.query.order_by(Movie.ranking.asc()) # asc
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()

    # print(all_movies)
    return render_template("index.html", movies=all_movies)


@app.route('/find')
def find():
    global RATING
    global REVIEW
    search_id = request.args.get('id')
    m_response = requests.get(
        url=f'https://api.themoviedb.org/3/movie/{search_id}?api_key={TMDB_API_KEY}&append_to_response=videos')
    movie_data = m_response.json()
    try:
        new_movie = Movie(
            title=movie_data['title'],
            year=movie_data['release_date'].split('-')[0],
            description=movie_data['overview'],
            rating=RATING,
            ranking=movie_data['vote_average'],
            review=REVIEW,
            trailer=f"https://www.youtube.com/watch?v={movie_data['videos']['results'][1]['key']}",
            img_url=f"https://image.tmdb.org/t/p/original{movie_data['poster_path']}"

        )
        db.session.add(new_movie)
        db.session.commit()
    except IndexError:
        print(IndexError)
        pass
    return redirect(url_for('home', ))


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = EditForm()
    if form.validate_on_submit():
        if request.method == "POST":
            movie_id = request.args.get('id')
            print(f"Movie id {movie_id}")
            update_movie = Movie.query.get(movie_id)
            update_movie.rating = form.rating.data
            update_movie.review = form.review.data
            db.session.commit()
        return redirect(url_for('home'))
    movie_id = request.args.get('id')
    movie_selected = Movie.query.get(movie_id)
    return render_template('edit.html', form=form, movie=movie_selected)


@app.route("/add", methods=["GET", "POST"])
def add():
    global QUERY_MOVIE
    form = AddForm()
    if form.validate_on_submit():
        if request.method == "POST":
            # search movie
            QUERY_MOVIE = form.title.data
            return redirect(url_for('select'))
    return render_template('add.html', form=form)


@app.route('/select')
def select():
    search_endpoint = f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=en-US&query={QUERY_MOVIE}&page=1&include_adult=false'
    response = requests.get(url=search_endpoint)
    search_data = response.json()['results']
    return render_template('select.html', data=search_data)


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    # DELETE A RECORD BY ID
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
