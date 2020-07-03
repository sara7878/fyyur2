
#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
#SARA

import logging
import sys
from logging import FileHandler, Formatter
import json
import os
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form

import babel
import dateutil.parser
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


db = SQLAlchemy()
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website=db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(120))
    
    shows = db.relationship('Show', backref='venue', lazy=True)


  
    def __repr__(self):
      return f'''<Venue id: {self.id} , name: {self.name} , city:{self.city} , state: {self.state} , 
      address: {self.address} , phone: {self.phone} , genres :{self.genres} , image_link: {self.image_link} , 
      facebook_link: {self.facebook_link}>'''





class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website=db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(120))

    shows = db.relationship('Show', backref='artist', lazy=True)


    def __repr__(self):
      return f'''<Artist id: {self.id} , name: {self.name} , city:{self.city} , state: {self.state} , 
      address: {self.address} , phone: {self.phone} , genres :{self.genres} , image_link: {self.image_link} , 
      facebook_link: {self.facebook_link}>'''


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)
    
    start_time = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)


    def __repr__(self):
      return f'<Show Artist_ID: {self.artist_id} , Venue_ID: {self.venue_id} , start_time: {self.start_time}>'
      


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
  data = []
  locations = set()
  date_now = datetime.now()
  venues = Venue.query.all()

  for venue in venues:
    locations.add((venue.city, venue.state))

  for location in locations:
    data.append({
        "city": location[0],
        "state": location[1],
        "venues": []
    })

  for venue in venues:
    num_upcoming_shows = 0
    shows = Show.query.filter_by(venue_id=venue.id).all()

    for show in shows:
      if show.start_time > date_now:
          num_upcoming_shows +=1

    for venue_location in data:
      if venue.city == venue_location['city'] and venue.state == venue_location['state']:
        venue_location['venues'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming_shows
        })
  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term','')
  venues=Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  response={}
  response['count']=len(venues)
  response['data']=venues
  return render_template('pages/search_venues.html', results=response,search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venue_id).all()
  past_shows=[]
  upcoming_shows=[]
  date_now = datetime.now()

  for show in shows:
    show_data = {
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": format_datetime(str(show.start_time))
        }
        
    if show.start_time > current_time:
      upcoming_shows.append(show_data)
    else:
      past_shows.append(show_data)

  data={
            'id': venue.id,
            'name': venue.name,
            'city': venue.city,
            'state': venue.state,
            'address': venue.address,
            'phone': venue.phone,
            'genres': venue.genres,  
            'image_link': venue.image_link,
            'facebook_link': venue.facebook_link,
            'website': venue.website,
            'seeking_talent': venue.seeking_talent,
            'seeking_description': venue.seeking_description,
            'past_shows':past_shows ,
            'upcoming_shows':upcoming_shows ,
            'past_shows_count':len(past_shows) ,
            'upcoming_shows_count': len(upcoming_shows),

        }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        venue = Venue()
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        temp_genres = request.form.getlist('genres')
        venue.genres = ','.join(temp_genres)
        venue.facebook_link = request.form['facebook_link']
        venue.website = request.form['website']
        venue.image_link=request.form['image_link']
        venue.seeking_description = request.form['seeking_description']
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')   

        else:
            flash('Venue ' + request.form['name'] +' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return None



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists=Artist.query.all()
  data=[]
  for artist in artists:
    data.append({
        "id": artist.id,
        "name": artist.name
    })
  return render_template('pages/artists.html',
                           artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term','')
  artists=Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()

  response={}
  response['count']=len(artists)
  response['data']=artists

  return render_template('pages/search_artists.html',
   results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id=artist_id).all()
  past_shows=[]
  upcoming_shows=[]
  date_now = datetime.now()

  for show in shows:
    show_data = {
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": format_datetime(str(show.start_time))
        }
    if show.start_time > current_time:
      upcoming_shows.append(show_data)
    else:
      past_shows.append(show_data)
  data={
            'id': artist.id,
            'name': artist.name,
            'city': artist.city,
            'state': artist.state,
            'phone': artist.phone,
            'genres': artist.genres,  
            'image_link': artist.image_link,
            'facebook_link': artist.facebook_link,
            'website': artist.website,
            'seeking_venue': artist.seeking_venue,
            'seeking_description': artist.seeking_description,
            'past_shows': past_shows,
            'upcoming_shows':upcoming_shows,
            'past_shows_count':len(past_shows),
            'upcoming_shows_count':len(upcoming_shows)

        }
  
  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.phone = request.form['phone']
    artist.facebook_link = request.form['facebook_link']
    artist.state = request.form['state']
    artist.seeking_description = request.form['seeking_description']
    artist.genres = request.form['genres']
    artist.website = request.form['website']
    artist.image_link = request.form['image_link']
    db.session.add(artist)
    db.session.commit()    
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form['name']    
    venue.phone = request.form['phone']
    venue.state = request.form['state']
    venue.facebook_link = request.form['facebook_link']
    venue.city = request.form['city']
    venue.address = request.form['address']
    venue.genres = request.form['genres']
    venue.seeking_description = request.form['seeking_description']
    venue.website = request.form['website']
    venue.image_link = request.form['image_link']
    db.session.add(venue)
    db.session.commit()
  except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    try:
        artist = Artist()
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.address = request.form['address']
        artist.phone = request.form['phone']
        temp_genres = request.form.getlist('genres')
        artist.genres = ','.join(temp_genres)
        artist.facebook_link = request.form['facebook_link']
        artist.website = request.form['website']
        artist.image_link=request.form['image_link']
        artist.seeking_description = request.form['seeking_description']
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')   

        else:
            flash('Venue ' + request.form['name'] +' was successfully listed!')
    return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append({
            'venue_id': show.venue_id,
            'venue_name': show.venues.name,
            'artist_id': show.artist_id,
            'artist_name': show.artists.name,
            'artist_image_link': show.artists.image_link,
            'start_time': show.start_time.isoformat()
        })
  

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        show = Show()
        show.venue_id = request.form['venue_id']
        show.artist_id = request.form['artist_id']
        show.start_time = request.form['start_time']
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Show could not be listed.')
        else:  
            flash('successfully listed')
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# Launch.
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
'''
