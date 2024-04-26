from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

class Base(DeclarativeBase):
    pass


# requests
movie_database_api_key = 'YOUR-TMDB APIKEY'
headers = {
    "accept": "application/json",
     "Authorization": "Bearer YOUR TMDB AUTH"
}

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
db.init_app(app)

class Base(DeclarativeBase):
    pass


class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String)
    rating: Mapped[int] = mapped_column(Integer)
    ranking: Mapped[int] = mapped_column(Integer)
    review: Mapped[str] = mapped_column(String)
    img_url: Mapped[str] = mapped_column(String)

class Edit(FlaskForm):
    rating = StringField(label='Rating', validators=[DataRequired()])
    review = StringField(label='Review', validators=[DataRequired()])
    submit = SubmitField(label='Update')

class Add(FlaskForm):
    movie = StringField(label='Movie Title', validators=[DataRequired()])
    submit = SubmitField(label='Add')


with app.app_context():
    db.create_all()


    @app.route("/", methods=['POST', 'GET'])
    def home():
        tail = db.session.execute(db.select(Movie).order_by(Movie.rating.desc())).scalars()
        return render_template("index.html", movies=tail)

    @app.route('/edit/<id>', methods=["POST", "GET"])
    def edit(id):
        form = Edit()
        if form.validate_on_submit():
            if request.method == 'POST':
                new = db.session.query(Movie).filter_by(id=id).first()
                new.rating = form.rating.data
                new.review = form.review.data
                db.session.commit()
                return redirect(url_for('home'))

        return render_template("edit.html", form=form)

    @app.route('/delete/<id>', methods=['POST', 'GET'])
    def delete(id):
        movie_id = id
        movie = db.session.query(Movie).filter_by(id=movie_id).first()
        db.session.delete(movie)
        db.session.commit()
        return redirect(url_for('home'))

    @app.route('/add', methods=["POST", "GET"])
    def add():
        form = Add()
        if request.method == 'POST':
            movie = request.form.get('movie')
            return redirect(url_for('select', movie_name=movie))

        return render_template('add.html', form=form)


    @app.route('/select/<movie_name>', methods=['POST', 'GET'])
    def select(movie_name):
        params = {
            'query': movie_name
        }
        response = requests.get(url='https://api.themoviedb.org/3/search/movie', headers=headers, params=params)
        result = response.json()
        movies = result['results']
        if request.method == 'POST':
            return redirect(url_for('mid'))
        return render_template('select.html', movies=movies)

    @app.route('/mid/<id>', methods=['POST', 'GET'])
    def mid(id):
        movie_id = id
        details_url = f'https://api.themoviedb.org/3/movie/{movie_id}'
        response = requests.get(url=details_url, headers=headers)
        movies = response.json()
        movie = Movie(
            title=movies['original_title'],
            img_url=movies['poster_path'],
            year=movies['release_date'],
            description=movies['overview'],
            rating='',
            ranking='',
            review=''
        )
        db.session.add(movie)
        db.session.commit()
        lib_id = movie.id

        return redirect(url_for('edit', id=lib_id))

if __name__ == '__main__':
    app.run(debug=True)
