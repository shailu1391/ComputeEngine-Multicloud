import os
import logging
import pandas as pd
import time
import http.client
from concurrent.futures import ThreadPoolExecutor
import math
import csv


from flask import Flask, request, render_template, make_response,jsonify
from random import sample

app = Flask(__name__)

# various Flask explanations available at:  https://flask.palletsprojects.com/en/1.1.x/quickstart/

def doRender(tname, values={}):
	if not os.path.isfile( os.path.join(os.getcwd(), 'templates/'+tname) ): #No such file
		return render_template('home.html')
	return render_template(tname, **values) 

@app.route('/hello')
# Keep a Hello World message to show that at least something is working
def hello():
	return 'Hello World!'
# Defines a POST supporting calculate route

@app.route('/random', methods=['POST'])
def RandomHandler():
		import http.client
		if request.method == 'POST':
				v = request.form.get('s')
				w = request.form.get('q')
				x = request.form.get('d')
				y = request.form.get('r')

				total_shots = v

				parallel = int(y)
				runs=[value for value in range(parallel)]

				def getpage(id):
					try:
						host = "xdn2f3nh2a.execute-api.us-east-1.amazonaws.com"
						c = http.client.HTTPSConnection(host)
						json= '{ "s": "'+v+'","q": "'+w+'","d": "'+x+'","r": "'+y+'"}'
						c.request("POST", "/default/piLambda", json)
 
						response = c.getresponse()
						data = response.read().decode('utf-8')
						import json
						data = json.loads(data)
						
						return data
						
					except IOError:
						print( 'Failed to open ', host ) # Is the Lambda address correct?
					print(data+" from "+str(id)) # May expose threads as completing in a different order
					return "page "+str(id)

				def getpages():
					with ThreadPoolExecutor() as executor:
						results=executor.map(getpage, runs)
					return results

				start = time.time()
				results = getpages()
				final_result = {}
				results=[x for x in results]
				print(results)
				elapsedtime= time.time() - start
				print( "Elapsed Time: ",elapsedtime)
				ecost = elapsedtime*0.0000021
				len_res = 0
				i=1
				for result in results:
					for k,v in result.items():
						final_result[k] = v if not final_result.get(k) else final_result[k] + v
						len_res = len(v)
					final_result['thread_id'] = [i for j in range(len_res)] if not final_result.get('thread_id') else final_result['thread_id'] +[i for j in range(len_res)]
					i=i+1

				
				final_result = pd.DataFrame.from_dict(final_result)
				finalPi = final_result["estimate_pi"].mean()

				def get_length(file_path):
					with open("datahistory.csv") as csvfile:
						reader=csv.reader(csvfile)
						reader_list = list(reader)
						print(reader_list)
						return len(reader_list)

				def append_history(file_path,s,q,d,parallel,pi,costpa):
					fieldnames=["sno.","Total Shots","Reporting Rate","Matching Digits","Resources","Final Pi","Cost"]
					next_id = get_length(file_path)
					with open(file_path,"a") as csvfile:
						writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
						writer.writerow({"sno.":next_id,"Total Shots":s,"Reporting Rate":q,"Matching Digits":d,"Resources":parallel,"Final Pi":pi,"Cost":costpa})
				
				#append_history("datahistory.csv",total_shots,w,x,parallel,finalPi,ecost)

				#a = round(math.pi,x)
				#b="a"

				#def match(finalPi,b):
					#if "finalPi" == b:
					#	return "Matches"
					#else:
					#	return "Does not Match"
				#message = match(finalPi,b)
							
		return render_template("tabletest.html",  tables=[final_result.to_html(classes='data')], titles=final_result.columns.values,content =elapsedtime,cost=ecost,finalval = finalPi)

@app.route('/output')
def storage():
	return render_template("output.html")

#@app.route('/piplot')
#def piplot():
#	return render_template("piplot.html")


# catch all other page requests - doRender checks if a page is available (shows it) or not (index)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def mainPage(path):
	return doRender(path)

@app.errorhandler(500)
# A small bit of error handling
def server_error(e):
	logging.exception('ERROR!')
	return """
	An  error occurred: <pre>{}</pre>
	""".format(e), 500

if __name__ == '__main__':
	# Entry point for running on the local machine
	# On GAE, endpoints (e.g. /) would be called.
	# Called as: gunicorn -b :$PORT index:app,
	# host is localhost; port is 8080; this file is index (.py)
	app.run(host='127.0.0.1', port=8080, debug=True)

   