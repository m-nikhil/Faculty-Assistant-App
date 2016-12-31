from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class availability(db.Model):
	__tablename__ = "availability"
	name = db.Column(db.String(50),primary_key=True)
	number = db.Column(db.Integer,default=0)
	

class booked(db.Model):
	__tablename__ = "booked"
	id = db.Column(db.Integer,primary_key =True, autoincrement=True, index=True)
	name = db.Column(db.String(50))
	by = db.Column(db.String(50),index=True)      #faculty ID
	date_of_booking = db.Column(db.Date,index=True,info={'min': datetime.date.today()})    #timestamp
	time_slot = db.Column(db.Enum('1','2','3','4','5','6','7')) #,'special'))
	date = db.Column(db.Date,info={'min': datetime.date.today()})
	quantity = db.Column(db.Integer)
	status = db.Column(db.Enum('booked','reservation'))


class user(db.Model):
	__tablename__ = "users"
	id = db.Column(db.String(50),primary_key = True)
	name = db.Column(db.String(50))
	password = db.Column(db.String(50),info={'min': 6})
	active = db.Column(db.Boolean, nullable=False, default=True)

	@property
	def is_authenticated(self):
		return True

	@property
	def is_active(self):
		return self.active

	def get_id(self):
		return unicode(self.id)

	def verify_password(self, in_password):
		#  return bcrypt.verify(in_password, self.pwhash)
		return in_password == self.password   


def load_db(db):
  db.drop_all()
  db.create_all()
  db.session.add_all([
  	user(id="1",name = "a",password="aa"),
  	user(id="2",name = "b",password="bb"),
  	availability(name="projector",number = "4"),
  	booked(name = "projector", by = "aa",time_slot = "3",quantity="1",date="2000-01-01", status="booked")
  ])
  db.session.commit()











	