from datetime import datetime
from dateutil.parser import parse
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, Optional, Regexp, ValidationError
import re
from urllib.parse import urlparse

# from flask_wtf import Form as ActualFlaskWTFFormClass
# from wtforms import Form as ActualWTFormsBaseClass

# print(f"---- forms.py Diagnostics ----")
# print(f"The class imported as 'Form' from 'flask_wtf' is: {ActualFlaskWTFFormClass}")
# print(f"Does ActualFlaskWTFFormClass have 'hidden_tag': {hasattr(ActualFlaskWTFFormClass, 'hidden_tag')}")
# print(f"Does ActualFlaskWTFFormClass have 'validate_on_submit': {hasattr(ActualFlaskWTFFormClass, 'validate_on_submit')}")
# print(f"The base Form class from 'wtforms' is: {ActualWTFormsBaseClass}")
# print(f"Is ActualFlaskWTFFormClass the same as ActualWTFormsBaseClass: {ActualFlaskWTFFormClass is ActualWTFormsBaseForm}")
# print(f"---------------------------")

def is_valid_phone(form, field):
    """
    Custom validator for phone numbers. Strips common non-digit characters
    and checks if the length is between 10 and 15 digits.
    """
    if not field.data:
        return # Allow empty phone numbers
        
    phone_number = re.sub(r'[()\s-]', '', field.data)

    if not phone_number.isdigit() or not (10 <= len(phone_number) <= 15):
        raise ValidationError("Invalid phone number. Please use a valid format like xxx-xxx-xxxx.")


def is_valid_url(form, field):
    """
    Custom validator for URLs. Allows URLs without a scheme (http/https).
    """
    if not field.data:
        return # Allow empty URLs

    url_text = field.data
    # Prepend http:// if no scheme is present
    if not url_text.lower().startswith(('http://', 'https://')):
        url_text = 'http://' + url_text
    
    try:
        # urlparse will check for basic structural validity
        result = urlparse(url_text)
        if not all([result.scheme, result.netloc]):
            raise ValidationError('Invalid URL format.')
    except:
        raise ValidationError('Invalid URL format.')


class FlexibleDateTimeField(DateTimeField):
    """
    Helper custome DateTimeField that parses flexible date/time formats
    and defaults to 10 PM if no time is provided.
    """
    def process_formdata(self, valuelist):
        if valuelist:
            date_str = " ".join(valuelist).strip()
            if not date_str:
                self.data = None
                return

            try:
                # Use dateutil.parser to understand most formats
                parsed_datetime = parse(date_str)
                
                # If the parser defaults time to midnight, the user likely only entered a date.
                # The 'default_hour' and 'default_minute' attributes from dateutil.parser.parse
                # are not straightforward to check, so we check the result.
                if parsed_datetime.hour == 0 and parsed_datetime.minute == 0 and parsed_datetime.second == 0:
                    # User likely only provided a date, so set default time to 10 PM.
                    self.data = parsed_datetime.replace(hour=22, minute=0, second=0)
                else:
                    self.data = parsed_datetime
            except (ValueError, TypeError):
                self.data = None

class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id', 
        validators=[DataRequired()]
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired()]
    )
    start_time = FlexibleDateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone',
        validators=[Optional(), is_valid_phone]
    )
    image_link = StringField(
        'image_link', validators=[Optional(), is_valid_url]
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=[
            ('Alternative', 'Alternative'),
            ('Blues', 'Blues'),
            ('Classical', 'Classical'),
            ('Country', 'Country'),
            ('Electronic', 'Electronic'),
            ('Folk', 'Folk'),
            ('Funk', 'Funk'),
            ('Hip-Hop', 'Hip-Hop'),
            ('Heavy Metal', 'Heavy Metal'),
            ('Instrumental', 'Instrumental'),
            ('Jazz', 'Jazz'),
            ('Musical Theatre', 'Musical Theatre'),
            ('Pop', 'Pop'),
            ('Punk', 'Punk'),
            ('R&B', 'R&B'),
            ('Reggae', 'Reggae'),
            ('Rock n Roll', 'Rock n Roll'),
            ('Soul', 'Soul'),
            ('Other', 'Other'),
        ]
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(), is_valid_url]
    )
    website_link = StringField(
        'website_link', validators=[Optional(), is_valid_url]
    )

    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = StringField(
        'seeking_description'
    )



class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    phone = StringField(
        # TODO implement validation logic for phone (DONE)
        'phone', 
        validators=[Optional(), is_valid_phone]
    )
    image_link = StringField(
        'image_link', validators=[Optional(), is_valid_url]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=[
            ('Alternative', 'Alternative'),
            ('Blues', 'Blues'),
            ('Classical', 'Classical'),
            ('Country', 'Country'),
            ('Electronic', 'Electronic'),
            ('Folk', 'Folk'),
            ('Funk', 'Funk'),
            ('Hip-Hop', 'Hip-Hop'),
            ('Heavy Metal', 'Heavy Metal'),
            ('Instrumental', 'Instrumental'),
            ('Jazz', 'Jazz'),
            ('Musical Theatre', 'Musical Theatre'),
            ('Pop', 'Pop'),
            ('Punk', 'Punk'),
            ('R&B', 'R&B'),
            ('Reggae', 'Reggae'),
            ('Rock n Roll', 'Rock n Roll'),
            ('Soul', 'Soul'),
            ('Other', 'Other'),
        ]
     )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[Optional(), is_valid_url]
     )

    website_link = StringField(
        'website_link', validators=[Optional(), is_valid_url]
     )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
     )

