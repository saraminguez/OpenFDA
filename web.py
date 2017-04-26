#Copyright [2017] [Sara Minguez Monedero]

#Licensed under the Apache License, Version 2.0 (the "License"); you may not #use this file except in compliance with the License. You may obtain a copy of #the License at

#http://www.apache.org/licenses/LICENSE-2.0

#Unless required by applicable law or agreed to in writing, software #distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the #License for the specific language governing permissions and limitations under #the License.

#solo boton ·#simepre se tiene que llmar web o server
import http.server
import http.client
import json

class OpenFDAClient(): 
	OPENFDA_API_URL="api.fda.gov"
	OPENFDA_API_EVENT='/drug/event.json'
	OPENFDA_API_DRUG='&search=patient.drug.medicinalproduct:'
	OPENFDA_API_COMPANY='&search=companynumb:'
	
	def get_event(limit='10'):
		##
		#GET EVENT
		##
		conn = http.client.HTTPSConnection(OpenFDAClient.OPENFDA_API_URL)
		conn.request("GET", OpenFDAClient.OPENFDA_API_EVENT + '?limit=' + limit)
		r1 = conn.getresponse()
		data1=r1.read()
		data=data1.decode("utf8")
		return json.loads(data)
		
	def get_drug_search(drug_search,limit='10'):
		conn = http.client.HTTPSConnection(OpenFDAClient.OPENFDA_API_URL)
		conn.request("GET", OpenFDAClient.OPENFDA_API_EVENT + '?limit='+ limit + OpenFDAClient.OPENFDA_API_DRUG + drug_search) #aunque se llame drug_search es una variable y lo puedo utilizar para lo que quiera
		r1 = conn.getresponse()
		data1=r1.read()
		data=data1.decode("utf8")
		return json.loads(data)

	def get_companies_search(company_search, limit='10'):
		conn = http.client.HTTPSConnection(OpenFDAClient.OPENFDA_API_URL)
		conn.request("GET", OpenFDAClient.OPENFDA_API_EVENT + '?limit='+ limit + OpenFDAClient.OPENFDA_API_COMPANY + company_search) #aunque se llame drug_search es una variable y lo puedo utilizar para lo que quiera
		r1 = conn.getresponse()
		data1=r1.read()
		data=data1.decode("utf8")
		return json.loads(data)
		
class OpenFDAParser(): 
	
	def get_drugs_from_events(diccionario):
		events= diccionario['results']
		drugs=[]
		for event in events:
			drugs += [event['patient']['drug'][0]['medicinalproduct']]
		return drugs

	def get_companies_from_events(diccionario): 
		events= diccionario['results']
		companies=[]
		for event in events:
			companies+=[event['companynumb']]
		return companies
		
	def get_patient_sex_from_events(diccionario): 
		events= diccionario['results']
		patients_sex=[]
		for event in events: 
			patients_sex+=[event['patient']['patientsex']]
		return patients_sex

class OpenFDAHTML(): 	
	def get_main_page():
		return """
		<html>
			<head>
				<title>OpenFDA Cool App</title>
			</head>
			<body>
				<h1>OpenFDA Client</h1>
				<form method="get" action="listDrugs">
					<input type = "submit" value="Drug List"></input>
					<input type="number" name="limit"></input>
				</form>
				<form method="get" action="searchCompany">
					<input type="text" name="company"></input>
					<input type="submit" value="Search companynumb"></input>
					<input type="number" name="limit"></input>
				</form>
				<form method="get" action="listCompanies">
					<input type = "submit" value="Companies List"></input>
					<input type="number" name="limit"></input>
					
				</form>
				<form method="get" action="searchDrug">
					<input type="text" name="drug"></input>
					<input type="submit" value="Search drug"></input>
					<input type="number" name="limit"></input>
				</form>
				<form method="get" action="listGender">
					<input type = "submit" value="Gender List"></input>
					<input type="number" name="limit"></input>
				</form>
			</body>
		</html>
		"""
	
	
	def get_error404_html():
		return """
		<html>
			<head>
				<title>OpenFDA Cool App</title>
			</head>
			<body>
				El recurso pedido no existe. </br>
			<a href='/'> Pagina principal</a>
			</body>
		</html>
		"""
		
	def get_list_html(items):
		html= """
		<html>
			<head>
				<title>OpenFDA Cool App</title>
			</head>
			<body>
				<ol>
		"""

		for item in items:
			html+= "<li>" + item + "</li>"

		html += """

				</ol>
			</body>
		</html>
		"""
		return html
	
#HTTPRequestHandler Class
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
		
	def URL_parser(self): 
		diccionario={}
		lista=self.path.split('?')
		if len(lista)<2: 
			return diccionario
		for item in lista[1].split('&'): 
			aux=item.split('=')
			diccionario[aux[0]]=aux[1]
		return diccionario
		
		
	def do_GET(self):
		main_page = False
		is_listdrugs = False
		is_listcompanies = False
		is_listpatient_sex=False
		is_search_company = False
		is_search_drug = False
		
		path = self.path.split('?')[0]
		if path == '/':
			main_page = True
		elif path == ('/listDrugs'):
			is_listdrugs = True
		elif path ==('/listCompanies'):
			is_listcompanies = True
		elif path == ('/listGender'):
			is_listpatient_sex = True
		elif path == ('/searchCompany'):
			is_search_company = True
		elif path == ('/searchDrug'):
			is_search_drug=True
		elif path == ('/secret'): 
			self.send_response(401)
			self.send_header('WWW-Authenticate','Basic realm= "My realm"')
			self.end_headers()
		elif path == ('/redirect'): 
			self.send_response(302)
			self.send_header('Location','/')
			self.end_headers()
		else: 
			self.send_response(404)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write(bytes(OpenFDAHTML.get_error404_html(), "utf8"))
			return


		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()

		html=OpenFDAHTML.get_main_page()

		if main_page: 
			self.wfile.write(bytes(html, "utf8")) 
		elif is_listdrugs:
			param_dic=self.URL_parser()
			if 'limit' in param_dic and param_dic['limit']!='': 
				event=OpenFDAClient.get_event(param_dic['limit'])
			else: 
				event=OpenFDAClient.get_event()
			drug=OpenFDAParser.get_drugs_from_events(event)
			html=OpenFDAHTML.get_list_html(drug)
			self.wfile.write(bytes(html, "utf8"))
		elif is_listcompanies:
			param_dic=self.URL_parser()
			if 'limit' in param_dic and param_dic['limit']!='': 
				event=OpenFDAClient.get_event(param_dic['limit'])
			else: 
				event=OpenFDAClient.get_event()
			company=OpenFDAParser.get_companies_from_events(event)
			html=OpenFDAHTML.get_list_html(company)
			self.wfile.write(bytes(html, "utf8"))
		elif is_listpatient_sex: 
			param_dic=self.URL_parser()
			if 'limit' in param_dic and param_dic['limit']!='': 
				event=OpenFDAClient.get_event(param_dic['limit'])
			else: 
				event=OpenFDAClient.get_event()
			patient_sex=OpenFDAParser.get_patient_sex_from_events(event)
			html=OpenFDAHTML.get_list_html(patient_sex)
			self.wfile.write(bytes(html, "utf8"))
		elif is_search_drug:
			param_dic=self.URL_parser()
			if 'drug' not in param_dic: 
				return 
			drug=param_dic['drug']
			if 'limit' in param_dic and param_dic['limit']!='': 
				event=OpenFDAClient.get_drug_search(drug,param_dic['limit'])
			else: 
				event=OpenFDAClient.get_drug_search(drug)
			companies=OpenFDAParser.get_companies_from_events(event)
			html=OpenFDAHTML.get_list_html(companies)
			self.wfile.write(bytes(html, "utf8"))
		elif is_search_company:
			param_dic=self.URL_parser()
			if 'company' not in param_dic: 
				return 
			companynumb=param_dic['company']
			if 'limit' in param_dic and param_dic['limit']!='': 
				event=OpenFDAClient.get_companies_search(companynumb,param_dic['limit'])
			else: 
				event=OpenFDAClient.get_companies_search(companynumb)
			drugs=OpenFDAParser.get_drugs_from_events(event)
			html=OpenFDAHTML.get_list_html(drugs)
			self.wfile.write(bytes(html, "utf8"))
	
		return
