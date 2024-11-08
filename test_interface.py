from flask import Flask, render_template, request, redirect, url_for
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import deepl

# Initialisation de l'application Flask
app = Flask(__name__)

# Mapping des pays aux langues (codes ISO-639-1)
English= ["Antigua and Barbuda", "Australia", "Bahamas", "Barbados","Belize","Brunei", "Botswana", "Canada","Cameroon","Curaçao","Cook Islands","Dominica","Eritrea", "Eswatini", "Fiji","In Swat","India", "Gambia", "Ghana", "Grenada", "Guyana", "Ireland", "Jamaica", "Kenya", "Kiribati", "Lesotho", "Liberia", "Malawi", "Malta", "Marshall Islands", "Mauritius", "Micronesia", "Namibia", "Nauru","Niue", "New Zealand", "Nigeria", "Palau", "Papua New Guinea", "Philippines","Pakistan", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "Seychelles", "Sierra Leone", "Singapore", "Solomon Islands", "South Africa", "South Sudan","Sudan", "Trinidad and Tobago","Tanzania","Tuvalu","Tonga","Uganda", "United Kingdom","Vanuatu","United States", "Zambia", "Zimbabwe"]
French= ["Belgium", "Benin", "Burkina Faso", "Burundi", "Cameroon-FR", "Canada-FR", "Central African Republic", "Chad", "Comoros", "Congo ","Djibouti","Equatorial Guinea","France", "Gabon", "Guinea", "Haiti", "Ivory Coast","Luxembourg", "Madagascar", "Mali", "Monaco", "Mauritius-FR","Niger", "Rwanda-FR", "Senegal", "Seychelles-FR", "Switzerland", "Togo","Vatican","Vanuatu-FR"]
Arabic= ["Algeria", "Bahrain", "Comoros-AR","Chad-AR","Djibouti-AR", "Egypt","Eritrea-AR","Iraq", "Jordan", "Kuwait", "Lebanon", "Libya", "Mauritania", "Morocco","Malta-AR", "Oman", "Palestine", "Qatar", "Saudi Arabia", "Somalia", "Sudan-AR", "Syria", "Tunisia", "United Arab Emirates", "Yemen"]
Spanish = ["Argentina", "Bolivia", "Chile", "Colombia", "Costa Rica", "Cuba", "Dominican Republic", "Ecuador", "El Salvador", "Equatorial Guinea-ES", "Guatemala", "Honduras", "Mexico", "Nicaragua", "Panama","Puerto Rico","Paraguay", "Peru", "Spain","Uruguay", "Venezuela"]
Russian = ["Russia","Belarus","Kazakhstan","Uzbekistan","Moldova","Armenia"]
Turkish=["Azerbaijan","Northem Cyprus","Kazakhstan-TR","Kyrgyzstan","Turkmenistan","Turkey"]
German =["Germany","Austria","Switzerland-DE","Liechtenstein","Luxembourg"]
Portugese =["Brazil","Angola","Cape Verde","Guinea-Bissau","Mozambique","Sao Tome and Pincipe","Portugal","East Timor"]
Dutch= ["Netherlands"]

# Template modifié pour inclure le rôle d'un agent marketing et les variables pour plus d'informations
template = """
You are a marketing agent promoting a product to a potential customer. Present the product in an engaging and persuasive manner with no more than 140 characters maximum.

Product Information:
- Product Name: {product_name}
- Type: {product_type}
- Store name:{store_name}
- Key Features: {key_features}
- Price: {price}
- Promotion:{promotion}
- offer duration : {offer_duration}
- priorities : {priorities}

Encourage the customer to take advantage of this great offer and highlight why it's the best deal for them.
INSTRUCTIONS :
DO NOT USE ANY EMOJIS AND NO QUOTING MARKS !
USE PRONOUM "WE" INSTEAD OF I
ENSURE THE RESPONSE IS WITHIN 140 CHARACTERS.
"""

model = OllamaLLM(model='mistral',num_predict = 35) #num_predict = 35 #limitation of 35 tokens for 140
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model
# Page d'accueil avec formulaire
@app.route('/')
def index():
    return render_template('index.html')

# Route pour gérer la soumission du formulaire
@app.route('/promote', methods=['POST'])

def promote_product():
    product_name = request.form['product_name']
    product_type = request.form['product_type']
    store_name = request.form['store_name']
    key_features = request.form['key_features']
    price = request.form['price']
    promotion = request.form['promotion']
    country = request.form['country']
    priorities = request.form['priorities']
    offer_duration = request.form.get('offer_duration')

    # Vérifier si le pays entré est dans le dictionnaire des langues
    if country in French:
        target_lang = "FR"
    elif country in English:
        target_lang = "EN-GB"
    elif country in Arabic:
        target_lang = "AR"
    elif country in Spanish:
        target_lang = "ES"
    elif country in Russian:
        target_lang = "RU"
    elif country in Portugese:
        target_lang = "PT-PT"
    elif country in German:
        target_lang = "DE"
    elif country in Turkish:
        target_lang = "TR"
    elif country in Dutch:
        target_lang = "NL"
    else:
        target_lang = "EN-GB"

    # Informations du produit à promouvoir
    product_info = {
        "product_name": product_name,
        "product_type": product_type,
        "store_name": store_name,
        "key_features": key_features,
        "price": price,
        "promotion": promotion,
        "offer_duration" : offer_duration,
        "priorities": priorities 
    }

    if offer_duration:
        product_info["promotion"] = offer_duration
    else :
        product_info["promotion"] = "No time duration"

    # Générer trois messages de promotion
    results = [chain.invoke(product_info)[:300] for _ in range(3)]

    # Initialisation du traducteur DeepL
    auth_key = '52d5f925-0c7a-45f0-8cbc-2254808f84c3:fx' 
    translator = deepl.Translator(auth_key)

    # Traduire chaque message
    translated_results = [translator.translate_text(result, target_lang=target_lang).text for result in results]

    return render_template('result.html', results=translated_results, country=country)

if __name__ == '__main__':
    app.run(debug=True)
