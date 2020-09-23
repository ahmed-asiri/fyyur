#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import Venue, Artist, Show, Artist_Genre, Venue_Genre, db, app, moment

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#



migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

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
  # TODO: replace with real venues data.
  venues = Venue.query.order_by(Venue.state, Venue.city).all()
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  prev_city = ''
  prev_state = ''
  data = []
  temp_venue = {}
  for venue in venues:

    if venue.city == prev_city and venue.state == prev_state:
      temp_venue['venues'].append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len(venue.shows_to_list()[0])

      })
    
    else:
      if prev_city != '':
        data.append(temp_venue.copy())
      prev_city = venue.city
      prev_state = venue.state
      temp_venue['city'] = venue.city
      temp_venue['state'] = venue.state
      temp_venue['venues'] = [
        {
          # add the upcoming shows using lambda expression
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': len(venue.shows_to_list()[0])
        }
      ]

  data.append(temp_venue)     
  print(data)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venues = Venue.query.filter(Venue.name.contains(request.form.get('search_term'))).all()
  response = {
   "count": len(venues),
   "data": [] 
  }

  for venue in venues:
    response["data"].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(venue.shows_to_list()[0])

    })
  print(response)

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter(Venue.id == venue_id).first()
  venue_view_data = venue.to_dict_view()
  return render_template('pages/show_venue.html', venue=venue_view_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()

  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  try:
    # creating new Venue object, and in pending state until commit happen  
    venue = Venue(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      address=request.form['address'],
      phone=request.form['phone'],
      facebook_link=request.form['facebook_link']
    )
    genres = request.form['genres']
    venue.add_genres(genres)
    
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as error:
    print(error)
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  # on successful db insert, flash success
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    shows = Show.query.filter(Show.venue_id == venue_id).all()
    for show in shows:
      db.session.delete(show)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except Exception as error:
    print(error)
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))




#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
      
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.order_by(Artist.name).all()
  data = []
  
  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name
    })      
  print(data)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".


  artists = Artist.query.filter(Artist.name.ilike("%"+request.form.get('search_term')+"%")).all()
  response = {
   "count": len(artists),
   "data": [] 
  }

  for artist in artists:
    response["data"].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcomin_shows": len(artist.shows_to_list()[0])
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  data_view = artist.to_dict_view()
  return render_template('pages/show_artist.html', artist=data_view)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist = Artist.query.get(artist_id)
  artist_view = artist.to_dict_view()
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.add_genres(request.form['genres'])
    phone = request.form['phone']
    facebook = request.form['facebook_link']
    if phone is not None:
      artist.phone = phone
    if facebook is not None:
      artist.facebook_link = facebook
    db.session.commit()
    flash('the Artist ' + artist.name + ' was successfully updated!')
  except Exception as error:
    print(error)
    db.session.rollback()
    flash('Artist ' + artist.name + 'cannot be updated, becasue something goes wrong, please try again!!')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  venue_view = venue.to_dict_view()

  return render_template('forms/edit_venue.html', form=form, venue=venue_view)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.add_genres(request.form['genres'])
    phone = request.form['phone']
    facebook = request.form['facebook_link']
    if phone is not None:
      venue.phone = phone
    if facebook is not None:
      venue.facebook_link = facebook
    db.session.commit()
    flash('the Venue ' + venue.name + ' was successfully updated!')
  except Exception as error:
    print(error)
    db.session.rollback()
    flash('Venue ' + venue.name + 'cannot be updated, becasue something goes wrong, please try again!!')
  finally:
    db.session.close()
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()

  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    artist = Artist(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      phone=request.form['phone'],
      facebook_link=request.form['facebook_link'],
      seeking_venue=False
    )
    genres = request.form['genres']
    artist.add_genres(genres)
    
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as error:
    print(error)
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append(show.to_dict_view())

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    show = Show(
      venue_id=request.form['venue_id'],
      artist_id=request.form['artist_id'],
      start_time=request.form['start_time']
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except Exception as error:
    print(error)
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
#if __name__ == '__main__':
#    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
