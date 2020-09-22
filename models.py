from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
import datetime

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:admin@localhost:5432/fyyur'
db = SQLAlchemy(app, session_options={"expire_on_commit": False})
db = SQLAlchemy(app, session_options={"expire_on_commit": False})


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
 

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    #adding website column
    website = db.Column(db.String(120), default="No Website") 
    #seeking talent state
    seeking_talent = db.Column(db.Boolean) 
    #seeking description column
    seeking_description = db.Column(db.String(120), default="No seeking for talents") 
    #genres relation
    genres = db.relationship('Venue_Genre', cascade="all,delete", backref='venue') 

    def add_genres(self, genres):
        # third normal form in SQL, result in other table called Venue_Genre, where
        # the genre is multi value not atomic
        if type(genres) is dict:
            for genre in genres:
                self.genres.append(Venue_Genre(
                    genre_type = genre
                ))
        else:
            self.genres.append(Venue_Genre(
                genre_type = genres
            ))
        
    def genre_to_list(self):
        #converting the genre into list, for view purpose
        genre_list = []
        for genre in self.genres:
            genre_list.append(genre.genre_type)
        return genre_list
    
    def shows_to_list(self):
        # sipliting the shows into two catogries, UPCOMING and PAST
        # by the date, and add them to list to return BOTH of them
        upcoming_list = []
        past_list = []
        for show in self.shows:
            show_data = {
                        "artist_id": show.artist.id,
                        "artist_name": show.artist.name,
                        "artist_image_link": show.artist.image_link,
                        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                        }
            if show.start_time > datetime.datetime.today():
                upcoming_list.append(show_data)
            else:
                past_list.append(show_data)
        shows_list = [upcoming_list, past_list]
        return shows_list
    
    def to_dict_view(self):
        # this method help to easily get the data in the proper
        # format for viewing purpose
        shows_list = self.shows_to_list()
        return {
            "id": self.id,
            "name": self.name,
            "genres": self.genre_to_list(),
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website,
            "facebook_link": self.facebook_link,
            "seeking_talent": self.seeking_talent,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
            "past_shows": shows_list[1],
            "upcoming_shows": shows_list[0],
            "upcoming_shows_count": len(shows_list[0]),
            "past_shows_count": len(shows_list[1])
        }

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    #website column added
    website = db.Column(db.String(120))
    #seeking state added as boolean
    seeking_venue = db.Column(db.Boolean)
    #seeking description added as String
    seeking_description = db.Column(db.String(200))
    #genres relation added
    genres = db.relationship('Artist_Genre', backref='artist')

    def shows_to_list(self):
        #getting the shows of the Artist in list, and categrize them UPCOMING and PAST
        # by the date, and add them to list to return BOTH of them
        upcoming_list = []
        past_list = []
        for show in self.shows:
            show_data = {
                        "venue_id": show.venues.id,
                        "venue_name": show.venues.name,
                        "venue_image_link": show.venues.image_link,
                        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                        }
            if show.start_time > datetime.datetime.today():
                upcoming_list.append(show_data)
            else:
                past_list.append(show_data)
        shows_list = [upcoming_list, past_list]
        return shows_list
    
    def genre_to_list(self):
        # third normal form in SQL, result in other table called Artist_Genre, where
        # the genre is multi value not atomic
        genre_list = []
        for genre in self.genres:
            genre_list.append(genre.genre_type)
        return genre_list

    def to_dict_view(self):
        # this method help to easily get the data in the proper
        # format for viewing purpose
        shows_list = self.shows_to_list()
        view_data={
            "id": self.id,
            "name": self.name,
            "genres": self.genre_to_list(),
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "facebook_link": self.facebook_link,
            "website": self.website,
            "seeking_venue": self.seeking_venue,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
            "past_shows": shows_list[1],
            "upcoming_shows": shows_list[0],
            "past_shows_count": len(shows_list[1]),
            "upcoming_shows_count": len(shows_list[0]),
        }
        return view_data
    
    def add_genres(self, genres):
        # when an Artist is just initiated, we add the genres by this method
        if type(genres) is dict:
            for genre in genres:
                self.genres.append(Artist_Genre(
                    genre_type = genre
                ))
        else:
            self.genres.append(Artist_Genre(
                genre_type = genres
            ))
        
        
# TODO: implement all Models

#Show model that, is the assossiated relation between Artist and Venue
#i use it as CLASS becasue there is start_time data field that i need it
# when ever i display the data, BTW it's still MANY TO MANY relationship
class Show(db.Model):
    __tablename__ = 'shows'
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime, primary_key=True)
    # relations
    venues = db.relationship(Venue, backref='shows' , cascade="all,delete")
    artist = db.relationship(Artist, backref='shows')

    def to_dict_view(self):
        # converting the Show data into easily readable dict format for the view
        return {
            "venue_id": self.venues.id,
            "venue_name": self.venues.name,
            "artist_id": self.artist.id,
            "artist_name": self.artist.name,
            "artist_image_link": self.artist.image_link,
            "start_time": self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }

# This relation show up from the third normal form, where the genres are Multi 
# value not atomic, so better to make it as relation
class Artist_Genre(db.Model):
    __tablename__ = 'Artist_Genre'
    genre_type = db.Column(db.String(), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)


# This relation show up from the third normal form, where the genres are Multi 
# value not atomic, so better to make it as relation
class Venue_Genre(db.Model):
    __tablename__ = 'Venue_Genre'
    genre_type = db.Column(db.String(), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)

      