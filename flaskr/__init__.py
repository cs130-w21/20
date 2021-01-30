import os

from flask import Flask, render_template, url_for, session, redirect, request

app = Flask(__name__, instance_relative_config=True)

# Secret key for session
app.config['SECRET_KEY'] = os.urandom(24)

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


# Home page
@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		# TODO: input validation
		stock_symbol = request.form['stock']
		volume = request.form['volume']
		
		# TODO: Send form results to DB, fetch all added stocks and display them
		dummy_stock_dict = {stock_symbol: volume} 
		return render_template('index.html', stock_dict=dummy_stock_dict)
		# return redirect(url_for('results'))
	else:
		return render_template('index.html', stock_dict=None)

# Results page (generates session id or code)
@app.route('/results')
def results():
	print(session)
	if 'code' in session:
		return render_template('results.html', code=session['code'], warning=True)
	else:
		code = 'QWERTY'  # TODO: generate random code
		session['code'] = code
		# TODO: Update DB here
		# Person sends link to partner
		print(session)
		return render_template('results.html', code=code)
		

@app.route('/waiting/<code>')
def wait_for_partner(code):
	# TODO: check if partner is done
	# if done, return redirect(url_for('partner_validated', code=code))
	# if not, return the results page again
	if 'code' in session:
		return redirect(url_for('results'))
	else:
		return 'yikes something went wrong'

@app.route('/compare/<code>')
def partner_validated(code):
	print(session)
	return 'partner finished'
