import os, string, secrets, sys, ast

from flask import (
	Flask, render_template, url_for, session, redirect, request,
	flash,
)
from finnhub import Client as make_client
from flaskr import algorithm
"""
Elvis' Finnhub API keys
Sandbox API Key: sandbox_c0bfrg748v6to0roveg0
Regular API Key: c0bfrg748v6to0rovefg

There are limits! See documentation:
https://finnhub.io/docs/api
"""

def create_app(test_config=None):
	"""
	Application factory function to set up the Flask application. Defines 
	the endpoints/routes for the application.

	#### Endpoints

	##### `@app.route('/', methods=['GET', 'POST'])`
	Returns index/home page with fields for updating stock portfolio.
	- **GET:** Returns index page.
	- **POST:** Updates stock portfolio in `session` with form input then renders index page. 
	Returns an error if stock symbol is invalid or the number of shares is not a positive integer.

	##### `@app.route('/about')`
	Returns About page.

	##### `@app.route('/compare/<code>', methods=['GET', 'POST'])`
	Returns compare page with input fields for UIDs of profiles to compare and computes compatability.
	- **GET:** Returns compare page. If `code` is not `<placeholder>`, then the first input field
	will have its initial value set to `code`.
	- **POST:** Fetches profiles for the input UIDs from the SQLite database, computes the 
	compatability between the profiles, stores this in `session`, then redirects to the 
	compatability page. Returns an error if both input IDs are the same or a profile does not 
	exist for either UID in the SQLite database.

	##### `@app.route('/results')`
	Generates a profile from stock portfolio stored in `session` and a UID, stores the profile + UID
	in the SQLite database, and returns the page displaying this information.

	- If no stock portfolio exists in `session`, this endpoint redirects to the index page.
	- Generating a profile / UID and persisting this information in the database is skipped 
	if the current stock portfolio in `session` remains unchanged from the last time a profile 
	was generated.

	##### `@app.route('/compat')`
	Returns page displaying compatability results.

	##### `@app.route('/remove/<key>')`
	Removes stock symbol `key` from `session` and redirects to index page.

	"""

	app = Flask(__name__, instance_relative_config=True)
	finnhub_client = make_client(api_key="c0bfrg748v6to0rovefg")

	# Load config (if it exists) or take a test config
	if test_config is None:
		app.config.from_mapping(
			SECRET_KEY=os.urandom(24),
			DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
		)
	else:
		app.config.from_mapping(test_config)
    # Ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# Initialize db
	from flaskr import db
	db.init_app(app)

	# Fix browser caching for css
	@app.context_processor
	def override_url_for():
		return dict(url_for=dated_url_for)

	def dated_url_for(endpoint, **values):
		if endpoint == 'static':
			filename = values.get('filename', None)
			if filename:
				file_path = os.path.join(app.root_path,
									 endpoint, filename)
				values['q'] = int(os.stat(file_path).st_mtime)
		return url_for(endpoint, **values)

	# Attempts to generate an unused UID within limit number of attempts.
	# If all attempts are expended (extremely unlikely to actually happen with default of 5),
	# the last generated UID is returned.
	def generate_uid(limit=5):
		uid = ""
		attempts = 0
		while attempts < limit:
			uid = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(10))
			if db.get_profile(uid) == None:
				break
			attempts += 1
		return uid

	# Home page
	@app.route('/', methods=['GET', 'POST'])
	def index():
		if request.method == 'POST':
			# DONE: input validation
			stock_symbol = request.form['stock'].upper()
			volume = request.form['volume']
			symbol_quote = finnhub_client.quote(stock_symbol)
			etf_country = finnhub_client.etfs_country_exp(stock_symbol)
			error = None
			if not volume.isdigit():
				error = "Number of Shares must be a positive integer"
			elif int(volume) < 1:
				error = "Number of Shares must be a positive integer"
			elif int(volume) > 1e20:
				error = "Number of Shares too large"
			elif symbol_quote['c'] == 0:
				error = "Invalid stock symbol: {}".format(stock_symbol)
			elif etf_country['symbol'] != '':
				error = "Cannot process ETF: {}".format(stock_symbol)

			# TODO: Send form results to DB, fetch all added stocks and display them
			# Code below uses Flask session to store data which can be moved to
			# DB later.
			if error is None:
				session['updated'] = True
				if 'stock_dict' in session:
					(session['stock_dict'])[stock_symbol] = volume
					session.modified = True
				else:
					session['stock_dict'] = {stock_symbol: volume}
				return render_template('index.html', stock_dict=session['stock_dict'])

			flash(error)
			if 'stock_dict' in session and session['stock_dict']:
				return render_template('index.html', stock_dict=session['stock_dict'])
			return render_template('index.html', stock_dict=None)
		else:
			if 'stock_dict' in session and session['stock_dict']:
				return render_template('index.html', stock_dict=session['stock_dict'])
			return render_template('index.html', stock_dict=None)

	# About page
	@app.route('/about')
	def about():
		return render_template('about.html')

	# Compare page
	@app.route('/compare/<code>', methods=['GET', 'POST'])
	def compare(code):
		if request.method == 'POST':
			uid1 = request.form['person1']
			uid2 = request.form['person2']
			person1 = db.get_profile(uid1)
			person2 = db.get_profile(uid2)
			error = None

			if uid1 == uid2:
				error = "IDs cannot be the same!"
			elif person1==None:
				error = "Invalid ID for first person"
			elif person2==None:
				error = "Invalid ID for second person"

			if error is None:
				# Convert db.get_profile string to dict
				p1 = ast.literal_eval(person1['profile']) # May still need sanitization
				p2 = ast.literal_eval(person2['profile'])

				session['compatPercent'] = algorithm.compare_profiles(p1, p2)
				print(session['compatPercent'])
				print("Compatibility Percentage: " + str(session['compatPercent']['COMPAT']), file=sys.stderr)

				return redirect(url_for('compat'))
			else:
				flash(error)
				return render_template('compare.html', code="")
		else:
			if code == '<placeholder>':
				return render_template('compare.html', code="")
			else:
				return render_template('compare.html', code=code)

	# Present_id page (generates session id or code)
	@app.route('/results')
	def results():
		person = {}
		if not 'stock_dict' in session:
			return redirect(url_for('index'))
		if session['updated']:
			person = algorithm.generate_profile(session['stock_dict'], finnhub_client)
			session['person'] = person

		# If code has already been generated and the input portfolio is unchanged,
		# skip code generation and persisting to db
		if 'code' in session and not session['updated']:
			return render_template('results.html', code=session['code'], warning=True, person=session['person'])
		else:

			# Generates a 10 character random string
			code = generate_uid()
			session['code'] = code

			db.create_profile(code, person)

			# Person sends link to partner
			print(session)
			session['updated'] = False
			return render_template('results.html', code=code, person=person)

	@app.route('/compat')
	def compat():
		results = session['compatPercent']
		return render_template('compat.html', results=results)

	# Remove stock symbol from table
	@app.route('/remove/<key>')
	def remove(key):
		if 'stock_dict' in session:
			session['stock_dict'].pop(key, None)
			session['updated'] = True
			session.modified = True
		return redirect(url_for('index'))

	return app
