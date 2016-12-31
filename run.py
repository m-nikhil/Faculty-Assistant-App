from flask import Flask, render_template, jsonify, request, render_template, flash, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy 
from models import *
from marshmallow import Schema
from flask.ext.restless import APIManager, ProcessingException 
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
import json



fas = Flask(__name__)

#------------------CONFIGURATION-----------------------
fas.config['SECRET_KEY'] = 'student assessment system'  #need to be changed

fas.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@127.0.0.1/fas'

db.init_app(fas)   # Bind SQLAlchemy to this Flask webapp
#--------------------------------------------------------
	
with fas.test_request_context():
   load_db(db)


#-----------------LOGIN MANAGEMENT-----------------------
login_manager = LoginManager()
login_manager.init_app(fas)

@login_manager.user_loader
def user_loader(id):
	return user.query.filter_by(id=id).first()
#------------------------------------------------------


#---------------------Login n logout-----------------------------

			
@fas.route("/login",methods=['GET','POST'])
def login():										#login with id and password

		if request.method == 'GET': 
			return render_template('login.html')

		username = request.form['username']
		password = request.form['password']
	
		user_accessed = user.query.filter_by(id=username).first()
	
		if user_accessed is None:
			flash(u'Username is incorrect')  # to log incorrect username
			return redirect(url_for('login'))
	
		if not user_accessed.verify_password(password):
			flash(u'Password is incorrect')  # to log incorrect password
			return redirect(url_for('login'))
		
		if not user_accessed.active:
			flash(u'Your account is inactive')  # to log inactive user
			return redirect(url_for('login'))
	
		login_user(user_accessed)
		flash('You were successfully logged in')
		return redirect(url_for('login'))



@fas.route("/logout")
@login_required
def logout():
	logout_user()
	flash('You were successfully logged out')
	return redirect(url_for('login'))

#-----------------------------------------------------------------------------------



def authentication(*args, **kwargs):
	if not current_user.is_authenticated:
		raise ProcessingException(description='Not authenticated!', code=401)
	return True


def booking(data=None, **kwargs):
	check_list = booked.query.filter_by(name = data['name'], date = data['date'], time_slot = data['time_slot'] )
	available = availability.query.filter_by(name = data['name'])
	count = 0
	for item in check_list:
		count+=item.quantity

	print count

	if(count+int(data['quantity']) > available[0].number):
		data['status'] = 'reservation'
	else:
		data['status'] = 'booked'

	return True

def trigger_reservation(instance_id=None, **kw):
		result = booked.query.filter_by(id=instance_id)
		status = result[0].status
		if(status == 'booked'):
			reservation_first = booked.query.filter_by(name = data['name'], date = data['date'], time_slot = data['time_slot'], status = 'reservation')
			if(reservation_first!=None):
				check_list = booked.query.filter_by(name = data['name'], date = data['date'], time_slot = data['time_slot'] )
				available = availability.query.filter_by(name = data['name'])
				count = 0
				for item in check_list:
					count+=item.quantity

				count -= result.quantity 

				for item in reservation:
					if(count+item.quantity <= available[0].number):
						to_change = booked.query.filter_by(id=item.id)
						to_change[0].status = 'booked'
						db.session.commit()
						return True
		return True


with fas.app_context():

	manager = APIManager(fas, flask_sqlalchemy_db=db,preprocessors={
                       'GET_SINGLE': [authentication],
                       'GET_MANY': [authentication],
                       'POST': [authentication],
                       'PUT_SINGLE': [authentication],
                       'PUT_MANY': [authentication],
                       'DELETE_SINGLE': [authentication],
                       'DELETE_MANY': [authentication]
                       })
	manager.create_api(availability, methods=['GET', 'POST', 'DELETE','PUT'],allow_patch_many=True, allow_delete_many=True)
	manager.create_api(booked, methods=['GET','POST','DELETE'],preprocessors={ 'POST': [booking], 'DELETE':[trigger_reservation] }) 
	#no put facility, delete and create new one
	#for post four parameters - name,date,time_slot and quantity
	#delete only by id
	manager.create_api(user, methods=['GET','POST','DELETE','PUT'],allow_patch_many=True, allow_delete_many=True)


	manager.create_api(reservation, methods=['GET'],allow_patch_many=True, allow_delete_many=True)
	#no delete facility, to delete use the delete from booked


# https://flask-restless.readthedocs.io/en/stable/requestformat.html#requestformat   (reference)


if __name__ == '__main__':
	fas.run(debug = True)
