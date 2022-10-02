# Import library for ReGex, SQLite, and Pandas
from email import charset
import re
import sqlite3
import pandas as pd

# Import library for Flask
from flask import Flask, jsonify
from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

# Define Swagger UI description
app = Flask(__name__)
app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info = {
    'title': LazyString(lambda: 'API Documentation for Data Processing'),
    'version': LazyString(lambda: '1.0.0'),
    'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing - Istiqlal Abadiyah Sukma Putri'),
    },
    host = LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)

# Connect to db
conn = sqlite3.connect('data/database.db', check_same_thread = False)
#conn.row_factory = sqlite3.Row
#mycursor = conn.cursor()

# Define and execute query for create table "data" if not exist
# Table "Data" contains "text" coloumn and "text_clean" coloumn. The two columns have "varchar" data type
conn.execute('''CREATE TABLE IF NOT EXISTS database (id INTEGER PRIMARY KEY AUTOINCREMENT, text varchar(255), text_clean varchar(255));''')


#WELCOME PAGE
@app.route('/', methods=['GET'])
def get():
  return "Welcome to Sukma's API!"


# Define endpoint for "input teks via form"
@swag_from("docs/contoh_text.yml", methods=['POST'])
@app.route('/contoh_text', methods=['POST'])
def text_processing():

    # Get text file
    text = request.form["text"]
    
    # Cleansing Process
    #remove_unnecessary_char
    text0 = re.sub('\n',' ',text) #Remove '\n'
    text1 = re.sub('rt',' ',text0) #Remove retweet symbol
    text2 = re.sub('user',' ',text1) #Remove username
    text3 = re.sub(r'pic.twitter.com.[\w]+', '', text2) #Remove pic 
    text4 = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text3) #Remove URL
    text5 = re.sub(r'#\s+', ' ', text4) #Remove hastag
    text6 = re.sub(r"@\s+", "", text5) #Remove mention
    text7 = re.sub('  +', ' ', text6) #Remove extra space

    #remove_nonaplhanumeric
    text8 = re.sub('[^0-9a-zA-Z]+', ' ', text7) 

    #remove_emoticon_byte
    text9 = text8.replace("\\", " ")
    text10 = re.sub('x..', ' ', text9)
    text11 = re.sub(' n ', ' ', text10)
    text12 = re.sub('\\+', ' ', text11)
    text_clean = re.sub('  +', ' ', text12)
    
    # Define and execute query for insert original text and cleaned text to sqlite database
    query_text = "INSERT INTO database(text, text_clean) values(?,?)"
    valtext = (text, text_clean)
    conn.execute(query_text, valtext)
    conn.commit()
    print(text)
    print(text_clean)

    select_data = conn.execute("SELECT * FROM database")
    conn.commit()
    data_text = [
        dict(id = row[0], text = row[1], text_clean = row[2])
        for row in select_data.fetchall() 
    ]

    return jsonify(data_text)


# Define endpoint for uploaded file CSV
@swag_from("docs/processing_file.yml", methods=['POST'])
@app.route("/upload_filecsv", methods=['POST'])
def upload_csv():
    #get csv file
    file = request.files['file']
    data = str(pd.read_csv(file, encoding='iso-8859-1'))
    
                        
    #Cleansing Process
    #remove_unnecessary_char
    data0 = re.sub('\n',' ',data) #Remove '\n'
    data1 = re.sub('rt',' ',data0) #Remove retweet symbol
    data2 = re.sub('user',' ',data1) #Remove username
    data3 = re.sub(r'pic.twitter.com.[\w]+', '', data2) #Remove pic 
    data4 = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',data3) #Remove URL
    data5 = re.sub(r'#\s+', ' ', data4) #Remove hastag
    data6 = re.sub(r"@\s+", "", data5) #Remove mention
    data7 = re.sub('  +', ' ', data6) #Remove extra space
      
    #remove_nonaplhanumeric
    data8 = re.sub('[^0-9a-zA-Z]+', ' ', data7) 
      
    #remove_emoticon_byte
    data9 = data8.replace("\\", " ")
    data10 = re.sub('x..', ' ', data9)
    data11 = re.sub(' n ', ' ', data10)
    data12 = re.sub('\\+', ' ', data11)
    data_clean = re.sub('  +', ' ', data12)

    # Define and execute query for insert original data and cleaned data to sqlite database
    query_files = "INSERT INTO database(text, text_clean) values(?,?)"
    valcsv = (data, data_clean)
    conn.execute(query_files, valcsv)
    conn.commit()
    print(data)
    print(data_clean)
    
    select_data = conn.execute("SELECT * FROM database")
    conn.commit()
    data_csv = [
        dict(id = row[0], text = row[1], text_clean = row[2])
        for row in select_data.fetchall() 
    ]
    return jsonify(data_csv)

    
if __name__ == '__main__':
   app.run()