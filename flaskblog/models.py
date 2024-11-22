from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskblog import SQLAlchemy, db, login_manager, app
from flask_login import UserMixin

db = SQLAlchemy()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# database setup
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    # backref allows us to get user who created post from post
    posts = db.relationship('Post', backref='author', lazy=True)


    # sends custom token for reset password, which is active for 30 minutes
    def get_reset_token(self, expires_sec = 1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
   
    @staticmethod # tells python to not expect self parameter as argument
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        # return user with user ID if token is valid (does not go to except)
        return User.query.get(user_id)
   
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Products(db.Model):
    __tablename__ = 'products'

    title = db.Column(db.String(255), nullable=False, primary_key=True)
    total_price = db.Column(db.Float, nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    availability = db.Column(db.String(50), nullable=False)
    source = db.Column(db.String(50), nullable=False, primary_key=True)
    link =  db.Column(db.Text)

    def __repr__(self):
        return f"Products('{self.title}', '{self.total_price}', '{self.price_per_unit}', '{self.unit}', '{self.availability}', '{self.link})"







