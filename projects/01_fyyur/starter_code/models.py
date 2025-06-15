from flask_sqlalchemy import SQLAlchemy
from flask import Flask #, render_template, request, redirect, url_for, jsonify, abort

from sqlalchemy.orm import backref
from flask_migrate import Migrate

from datetime import datetime
from enums import StateTypes, GenreTypes 


db = SQLAlchemy()

def init_db(app):
    app.config.from_object('config')
    db.init_app(app)
    migrate = Migrate(app, db)
    return db

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.Enum(StateTypes), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String), nullable=False) #added 
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(500))
    #artists = db.relationship("Artist", secondary="show", backref="Venues", lazy=True, cascade="all, delete-orphan")
    
    shows = db.relationship('Show', backref='venue', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f'<Venue: {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String)) # updated/added 
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # added below
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref='artist', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Artist: {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
   __tablename__ = 'show'

   id = db.Column(db.Integer, primary_key=True)
   # name = db.Column(db.String(120)) #not needed
   # venue_image_link = db.Column(db.String(500))
   start_time = db.Column(db.DateTime)
   
   venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
   artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
   
   def __repr__(self):
        return f'<Show: {self.id} Artist: {self.artist_id} Venue: {self.venue_id}>'