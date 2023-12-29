from flask import render_template, request, session, redirect, jsonify, url_for, flash
from flask import current_app as app
from application.database import db
from application.models import *
from passlib.hash import sha256_crypt
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask import request
from datetime import datetime


@app.route("/")
def home():
    if "user" in session:
        return render_template("home.html", user=session["user"], signed=True)
    else:
        return render_template("home.html", user="None", signed=False)


class UploadForm(FlaskForm):
    audio = FileField(
        "Audio File",
        validators=[
            FileRequired(),
            FileAllowed(
                ["mp3", "wav", "ogg"], "Only MP3, WAV, and OGG files are allowed."
            ),
        ],
    )


@app.route("/upload/<int:album_id>", methods=["GET", "POST"])
def upload(album_id):
    if request.method == "POST":
        audio_file = request.files["audio"]
        songname = request.form["songname"]
        songlyrics = request.form["songlyrics"]
        songduration = request.form["songduration"]
        if audio_file:
            new_song = Song(
                name=songname,
                lyrics=songlyrics,
                duration=songduration,
                audio=audio_file.filename,
                date_created=datetime.utcnow(),
                parent=album_id,
            )

            db.session.add(new_song)
            db.session.commit()

            return redirect(url_for("manage_album"))

    return render_template("upload.html")


@app.route("/register", methods=["GET", "POST"])
def user_registration():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User(name=username, password=password)
        db.session.add(user)
        db.session.commit()
        session["user"] = username
        return redirect("/login")

    return render_template("register.html", error_message="", x="User")


@app.route("/register/manager", methods=["GET", "POST"])
def manager_registration():
    if "manager" in session:
        return redirect("/")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        manager = Manager.query.filter_by(username=username).first()
        if manager:
            return render_template(
                "registration.html", error_message="Username already exists"
            )

        new_manager = Manager(username=username, password=password)
        db.session.add(new_manager)
        db.session.commit()

        return redirect(url_for("login"))
    else:
        return render_template("register.html", error_message="", x="Manager")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(name=username).first()
        if user and sha256_crypt.verify(password, user.password):
            session["user"] = user.name
            return redirect(url_for("market"))

        manager = Manager.query.filter_by(username=username).first()
        if manager and sha256_crypt.verify(password, manager.password):
            session["user"] = manager.username
            return redirect(url_for("manage_album"))

        return render_template(
            "login.html", error_message="Invalid username or password"
        )

    return render_template("login.html", error_message="")


@app.route("/create_playlist", methods=["POST"])
def create_playlist():
    if request.method == "POST":
        playlist_name = request.form.get("playlist_name")

        # Check if playlist_name is not None and not empty
        if playlist_name:
            user = User.query.filter_by(name=session["user"]).first()
            playlist = Playlist(name=playlist_name, user_id=user.id)
            db.session.add(playlist)
            db.session.commit()
            return redirect(url_for("playlist"))
        else:
            # Handle the case where playlist_name is None or empty
            flash("Please provide a valid playlist name", "error")

    return render_template("create_playlist.html")


@app.route("/playlist")
def playlist():
    # Query all playlists from the database
    playlists = Playlist.query.all()

    return render_template("playlist.html", playlists=playlists)


@app.route("/delete_playlist/<int:playlist_id>", methods=["POST"])
def delete_playlist(playlist_id):
    # Retrieve the playlist by ID
    playlist = Playlist.query.get_or_404(playlist_id)

    try:
        # Delete the playlist and commit the changes
        db.session.delete(playlist)
        db.session.commit()

        flash("Playlist deleted successfully", "success")
        return redirect(url_for("playlist"))
    except Exception as e:
        # Handle any exceptions, and optionally log the error
        flash("An error occurred while deleting the playlist", "error")
        # Log the error, e.g., print(e)

    return redirect(url_for("playlist"))


@app.route("/add_songs/<int:playlist_id>", methods=["GET", "POST"])
def add_songs(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)

    if request.method == "POST":
        # Assuming you have a form that allows users to select songs
        selected_song_ids = request.form.getlist("selected_songs")

        # Assuming you have a relationship between Playlist and Song
        selected_songs = Song.query.filter(Song.id.in_(selected_song_ids)).all()

        # Add the selected songs to the playlist
        playlist.songs.extend(selected_songs)
        db.session.commit()

        flash("Songs added to the playlist successfully", "success")
        return redirect(url_for("playlist"))

    # Get all songs for display in the template
    all_songs = Song.query.all()

    return render_template("add_song.html", playlist=playlist, all_songs=all_songs)


@app.route("/market")
def market():
    albums = Album.query.all()
    song = Song.query.all()
    return render_template(
        "userdashboard.html",
        albums=albums,
        song=song,
        user=session["user"],
    )


@app.route("/create_album", methods=["GET", "POST"])
def manage_album():
    if request.method == "POST":
        album_name = request.form["album_name"]
        genre = request.form["album_genre"]
        artist = request.form["album_artist"]
        manager = Manager.query.filter_by(username=session["user"]).first()
        album = Album(name=album_name, creator=manager, genre=genre, artist=artist)
        db.session.add(album)
        db.session.commit()

    albums = Album.query.all()
    return render_template("market.html", albums=albums, user=session["user"])


@app.route("/edit_album/<int:album_id>", methods=["GET", "POST"])
def edit_album(album_id):
    if request.method == "POST":
        new_album_name = request.form.get("album_name")
        new_album_genre = request.form.get("album_genre")
        new_album_artist = request.form.get("album_artist")
        album = Album.query.get(album_id)
        if not album:
            raise ValueError("Album not found")
        album.name = new_album_name
        album.genre = new_album_genre
        album.artist = new_album_artist
        db.session.commit()
        return redirect(url_for("manage_album"))
    return render_template("edit_album.html")


@app.route("/delete_album/<int:album_id>", methods=["POST"])
def delete_album(album_id):
    album = Album.query.get(album_id)
    if album:
        db.session.delete(album)
        db.session.commit()

    return redirect(url_for("manage_album"))


# @app.route("/create_song/<int:album_id>", methods=["POST", "GET"])
# def create_song(album_id):
#     if request.method == "POST":
#         song_name = request.form["song_name"]
#         unit = request.form["unit"]
#         rate = float(request.form["rate"])
#         quantity = int(request.form["quantity"])
#         song = Song(
#             name=song_name,
#             unit=unit,
#             rate=rate,
#             quantity=quantity,
#             parent=album_id,
#         )
#         db.session.add(song)
#         db.session.commit()

#         return redirect(url_for("manage_album"))
#     else:
#         return render_template("create_song.html")


@app.route("/delete_song/<int:song_id>", methods=["POST"])
def delete_song(song_id):
    song = Song.query.get(song_id)
    if song:
        db.session.delete(song)
        db.session.commit()
    return redirect(url_for("manage_album"))


# @app.route("/edit_album/<int:album_id>", methods=["GET", "POST"])
# def edit_album(album_id):
#     if request.method == "POST":
#         new_c_name = request.form.get("album_name")
#         album = Album.query.get(album_id)
#         if not album:
#             raise ValueError("album not found")
#         album.name = new_c_name
#         db.session.commit()
#         return redirect(url_for("manage_album"))
#     return render_template("edit_album.html")


# @app.route("/delete_album/<int:album_id>", methods=["POST"])
# def delete_album(album_id):
#     album = album.query.get(album_id)
#     if album:
#         db.session.delete(album)
#         db.session.commit()

#     return redirect(url_for("manage_album"))


@app.route("/songs")
def songs():
    all_songs = Song.query.all()
    return render_template("songs.html", songs=all_songs)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))
