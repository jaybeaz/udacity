#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import ArtistForm, VenueForm, ShowForm
# My imports below
from flask_migrate import Migrate
from sqlalchemy.orm import backref, joinedload # see: https://stackoverflow.com/questions/26475977/flask-sqlalchemy-adjacency-list-backref-error
from models import db, Venue, Artist, Show, init_db # from models.py
from enums import *
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

db = init_db(app)
app.config.from_object('config')
#db = SQLAlchemy(app) #comes from models.py
#db.init(app)
#migrate = Migrate(app, db)


# DONE: connect to a local postgresql database

# ? HOW TO USE MIGRATION in the cmd line <<< NOTE TO MY SELF :) >>>
#--> use [ flask db init ] to create a migration
#--> use [ flask db migrate ] to sync models
#--> use [ flask db upgrade ] and [ flask db downgrade ] to upgrade & downgrade versions of migrations

# DONE: connect to a local postgresql database ✅
#----------------------------------------------------------------------------#
# Models ---> MOVED TO models.py file
#----------------------------------------------------------------------------#



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
     date = dateutil.parser.parse(value)
  else:
     date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # data = Venue.query.all()
  areas_query = db.session.query(
                  Venue.city, Venue.state).distinct().all()
  data = []
  for area_tuple in areas_query:
    city, state = area_tuple
    venues_in_area = Venue.query.filter_by(city=city, state=state).all()
    # Add logic here to count upcoming shows for each venue if needed by the template
    # For now, the template pages/venues.html doesn't seem to use num_upcoming_shows
    data.append({
        "city": city,
        "state": state,
        "venues": venues_in_area 
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get("search_term", "").strip()
  print("---------------------------")
  print(f"Search term received: '{search_term}'")
  search_pattern = f'%{search_term}%'

  print(f"SQLAlchemy ILIKE pattern: '{search_pattern}'")

  venues = Venue.query.filter(Venue.name.ilike(search_pattern)).all()

  print(f"Venues found: {venues}")
  print("---------------------------")

  response = {
    "count": len(venues),
    "data": venues
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.get(venue_id)

  venue = db.session.query(Venue).options(
    joinedload(Venue.shows).joinedload(Show.artist)
    ).filter(Venue.id == venue_id).first_or_404()

  if not venue:
    return abort(404)

  now = datetime.utcnow()
  past_shows = []
  upcoming_shows = []

  for show in venue.shows:
    artist = show.artist
    show_details = {
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.isoformat() 
    }

    if show.start_time < now:
      past_shows.append(show_details)
    else:
      upcoming_shows.append(show_details)

  venue.past_shows = past_shows
  venue.upcoming_shows = upcoming_shows
  venue.past_shows_count = len(past_shows)
  venue.upcoming_shows_count = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  form = VenueForm(request.form)
  if form.validate_on_submit():
    try:
      new_venue = Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        image_link = form.image_link.data,
        genres = form.genres.data,
        facebook_link = form.facebook_link.data,
        website = form.website_link.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data
      )
      db.session.add(new_venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
      error = True
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      print(f"Error creating new Venue: {e}")
      print(sys.exc_info())
    finally:
      db.session.close()
  else:
    flash('An error occurred due to form validation. Please check the fields and try again.')
    for field, errors in form.errors.items():
      for error in errors:
        flash(f"Error in: {getattr(form, field).label.text} -> {error}", 'error')
    return render_template('forms/new_venue.html', form=form)
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  try:
    data = Artist.query.all()
  except Exception as e:
    print(F'Error: {str(e)}')
    print(sys.exc_info())
    data =[{
            "id": 4,
            "name": F"FAILED ARTISTS (EXCEPTION: {str(e)})",
          }]

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get("search_term")
  search_pattern = f'%{search_term}%'
  artists = Artist.query.filter(Artist.name.ilike(search_pattern)).all()
  response = {
    "count": len(artists),
    "data": artists
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # DONE: replace with real artist data from the artist table, using artist_id
  artist_data = Artist.query.get(artist_id)

  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(obj=artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get_or_404(artist_id)

  form = ArtistForm(request.form)
  if form.validate_on_submit():
    try:
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres = form.genres.data
      artist.image_link = form.image_link.data
      artist.facebook_link = form.facebook_link.data
      artist.website_link = form.website_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except Exception as e:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
      print(f"Error updating artist: {e}")
    finally:
      db.session.close()
  else:
    flash('An error occurred due to form validation. Please check the fields and try again.')
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(obj=venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(request.form)
  if form.validate_on_submit():
    try:
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.image_link = form.image_link.data
      venue.genres = form.genres.data
      venue.facebook_link = form.facebook_link.data
      venue.website = form.website.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except Exception as e:
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
      print(f"Error updating artist: {e}")
    finally:
      db.session.close()
  else: 
    flash('An error occurred due to form validation. Please check the fields and try again.')
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  print(f"---- app.py create_artist_form() Diagnostics (GET) ----") # Added (GET) for clarity
  print(f"Type of 'form' object: {type(form)}")
  print(f"Form object's MRO: {type(form).mro()}")
  print(f"Does form object have 'hidden_tag': {hasattr(form, 'hidden_tag')}")
  print(f"Does form object have 'validate_on_submit': {hasattr(form, 'validate_on_submit')}")
  print(f"Is form.hidden_tag callable: {callable(getattr(form, 'hidden_tag', None))}")
  print(f"Is form.validate_on_submit callable: {callable(getattr(form, 'validate_on_submit', None))}")
  print(f"------------------------------------")
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  form = ArtistForm(request.form)
  if form.validate_on_submit():
    try:
      new_artist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        genres = form.genres.data, # This comes as a list from SelectMultipleField
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        website_link = form.website_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data
      ) 
      db.session.add(new_artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
      error = True
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      print(f"Error creating new Arstist: {e}")
      print(sys.exc_info())
    finally:
      db.session.close()
  else:
    flash('An error occurred due to form validation. Please check the fields and try again.')
    for field, errors in form.errors.items():
      for error in errors:
        flash(f"Error in: {getattr(form, field).label.text} -> {error}", 'error')
    return render_template('forms/new_artist.html', form=form)
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  shows_query = db.session.query(Show).join(Artist).join(Venue).order_by(Show.start_time.desc()).all()
  shows_data = []
  for show in shows_query:
    shows_data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
      })

  return render_template('pages/shows.html', shows=shows_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  form = ShowForm(request.form)
  if form.validate_on_submit():
    try:
      new_show = Show(
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data,
        start_time = form.start_time.data
      )
      db.session.add(new_show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    except Exception as e:
      error = True
      db.session.rollback()
      flash('An error occurred. Show for artist: ' + request.form['artist_id'] + ' could not be listed.')
      print(f"Error creating new Show: {e}")
      print(sys.exc_info())
    finally:
      db.session.close()
  else:
    flash('An error occurred due to form validation. Please check the fields and try again.')
    for field, errors in form.errors.items():
      for error in errors:
        flash(f"Error in: {getattr(form, field).label.text} -> {error}", 'error')
    return render_template('forms/new_show.html', form=form)
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=3000)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
