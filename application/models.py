from application.database import db
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from datetime import datetime

# Association Table for many-to-many relationship between Playlist and Song
playlist_song_association = db.Table(
    "playlist_song_association",
    db.Column("playlist_id", db.Integer, db.ForeignKey("playlist.id")),
    db.Column("song_id", db.Integer, db.ForeignKey("song.id")),
)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    playlists = db.relationship("Playlist", backref="user", lazy=True)

    def __init__(self, name, password):
        self.name = name
        self.password = sha256_crypt.hash(password)


class Manager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    album = db.relationship("Album", backref="creator")

    def __init__(self, username, password):
        self.username = username
        self.password = sha256_crypt.hash(password)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    maker = db.Column(db.Integer, db.ForeignKey("manager.id"))
    genre = db.Column(db.String, nullable=False)
    artist = db.Column(db.String, nullable=False)
    song = db.relationship("Song", backref="album", lazy=True)

    def __repr__(self):
        return self.name


# ... (previous code)


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lyrics = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.Float, nullable=False)
    audio = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    parent = db.Column(db.Integer, db.ForeignKey("album.id"))
    playlists = db.relationship(
        "Playlist", secondary=playlist_song_association, back_populates="songs"
    )

    def __repr__(self):
        return self.name


# ... (rest of the code)


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    songs = db.relationship(
        "Song", secondary=playlist_song_association, back_populates="playlists"
    )
