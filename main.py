import sys
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel,
                               QLineEdit, QPushButton, QVBoxLayout,
                               QInputDialog)

from PyQt5.QtCore import Qt         # to work with alignement
import sqlite3
from datetime import datetime
import json
import csv




class WeatherApp(QWidget):          
    def __init__(self):
        super().__init__()          # arguments to send to parent

        # promt user to select options
        self.city_label = QLabel("Enter city name: ", self)
        self.city_input = QLineEdit(self)                           # create textbox
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.view_data_button = QPushButton("View Saved Weather", self)
        self.update_data_button = QPushButton("Update Description by ID", self)
        self.delete_data_button = QPushButton("Delete Record by ID", self)
        self.export_data_button = QPushButton("Export Weather Data", self)




        self.initUI()                                               # format and design layout
        self.weather_table()                                        # create DB table


    # define a method to initialize user interface
    def initUI(self):
        self.setWindowTitle("Weather App")

        vbox = QVBoxLayout()                                        # vertical layout manager to handle widgets

        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)
        vbox.addWidget(self.view_data_button)
        vbox.addWidget(self.update_data_button)
        vbox.addWidget(self.delete_data_button)
        vbox.addWidget(self.export_data_button)


        self.setLayout(vbox)                                        # pass in the layout manager
        
        # center align widgets
        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        # css styling
        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")

        # set stylesheet
        self.setStyleSheet("""
            QLabel, QPushButton{                        
                           font=family: calibri; 
            }
                           
            QLabel#city_label{
                           font-size: 40px;
                           font-style: italic;
            }
                           
            QLineEdit#city_input{
                           font-size: 40px;
            }
                           
            QPushButton#get_weather_button{
                           font-size: 30px;
                           font-weight: bold;     
            }
                           
            QLabel#temperature_label{
                           font-size: 75px;
            }
            QLabel#emoji_label{
                           font-size: 100px;
                           font-family: Segoe UI emoji;
            }

            QLabel#description_label{
                           font-size: 40px;
            }

        """)

        # connect our button with signal of clicked to slot (get_weather)
        self.get_weather_button.clicked.connect(self.get_weather) 

        self.view_data_button.clicked.connect(self.read_from_database)
        self.update_data_button.clicked.connect(self.update_description)
        self.delete_data_button.clicked.connect(self.delete_record)
        self.export_data_button.clicked.connect(self.export_data)



    def get_weather(self):
        
        api_key = "YOUR API KEY"    # openweathermap api            
        city = self.city_input.text()                   # get text from textbox (LineEdit widget)
        # api request to
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        try:
            response = requests.get(url)
            # raise expection as try block doesn't catch itself
            response.raise_for_status()
            data = response.json()                      # convert to json
            print(data)

            if data["cod"] == 200:
                self.display_weather(data)

        # exception raised by request module when HTTP request is within status code 400-500
        except requests.exceptions.HTTPError as HTTP_error:                               
            match response.status_code:
                case 400:
                    self.display_errors("Bad Request:\nPlease check your input")
                case 401:
                    self.display_errors("Unauthorized:\nInvalid API Key")
                case 403:
                    self.display_errors("Forbidden:\nAccess Denied")
                case 404:
                    self.display_errors("Not Found:\nCity not found")
                case 500:
                    self.display_errors("Internet Server Down:\nPlease try again later")
                case 502:
                    self.display_errors("Bad Gateway:\nInvalid response from server")
                case 503:
                    self.display_errors("Service unavailable:\nServer in down")
                case 504:
                    self.display_errors("Gateway timeout:\nNo response from server")
                case _:                                                     # in case no error matches
                    self.display_errors(f"HTTP error occured\n{HTTP_error}")

        # handle connection error          
        except requests.exceptions.ConnectionError:
            self.display_errors("Connection Error:\nCheck your internet connection")

        # handle timeout     
        except requests.exceptions.Timeout:
            self.display_errors("Timeout Error:\nThe request is timed out")
 
        except requests.exceptions.TooManyRedirects:
            self.display_errors("Too many request:\nCheck the URL")
        
        # error due to network/invalid url
        except requests.exceptions.RequestException as req_error:
            self.display_errors(f"Request Error:\n{req_error}")


    def display_errors(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)

        self.emoji_label.clear()
        self.description_label.clear()

    def display_weather(self, data):
        
        self.temperature_label.setStyleSheet("font-size: 75px;")
        temperature_k = data["main"]["temp"]
        temperature_c = temperature_k - 273.15
        temperature_f = (temperature_k * 9/5) - 459.67

        # temparature display
        self.temperature_label.setText(f"{temperature_c:.0f}°C")

        # description display
        weather_description = data["weather"][0]["description"]
        self.description_label.setText(f"{weather_description}")

        # emoji display
        weather_id = data["weather"][0]["id"]
        self.emoji_label.setText(self.display_emoji(weather_id))

        # store data to DB
        self.save_to_database(self.city_input.text(), temperature_c, weather_description)


    @staticmethod
    def display_emoji(weather_id):

        if 200<= weather_id <= 232:
            return "⛈️"
        elif 300 <= weather_id <= 321:
            return "⛅"
        elif 500 <= weather_id <= 531:
            return "☔"
        elif 600 <= weather_id <= 622:
            return "🌨️"
        elif 701 <= weather_id <= 741:
            return "🌁"
        elif weather_id == 762:
            return "🌋"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 781:
            return "🌪️"
        elif weather_id == 800:
            return "☀️"
        elif 801 <= weather_id <= 804:
            return "☁️"
        else:
            return ""
        

    # create weather data table
    def weather_table(self):
        try:
            conn = sqlite3.connect("weather_app.db")
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                temperature REAL NOT NULL,
                description TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            self.display_errors(f"DB Init Error: {e}")

    # save contents to DB
    def save_to_database(self, location, temperature_c, description):
        try:
            conn = sqlite3.connect("weather_app.db")
            cursor = conn.cursor()

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
            INSERT INTO weather_data(location, temperature, description, timestamp)
            VALUES (?,?,?,?)
            """, (location, round(temperature_c, 2), description, timestamp))

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            self.display_errors(f"DB Error: {e}")

    # get data from DB
    def read_from_database(self):
        try:
            conn = sqlite3.connect('weather_app.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM weather_data ORDER BY timestamp DESC")
            records = cursor.fetchall()
            conn.close()

            if not records:
                self.display_errors("No data found in the database.")
                return

            formatted = "\n\n".join(
                f"ID: {r[0]} | {r[4]}\nLocation: {r[1]}\nTemp: {r[2]}°C\nDesc: {r[3]}"
                for r in records[:5]  # limit to last 5 for readability
            )

            
            self.temperature_label.setStyleSheet("font-size: 50px;")
            self.temperature_label.setText("Recent Records")
            self.emoji_label.clear()
            self.description_label.setText(formatted)

        except sqlite3.Error as e:
            self.display_errors(f"DB Error: {e}")

    # update data description in DB
    def update_description(self):
        id_to_update, ok = QInputDialog.getInt(self, "Update Record", "Enter Record ID:")
        if not ok:
            return

        new_desc, ok = QInputDialog.getText(self, "Update Description", "Enter new description:")
        if not ok or not new_desc.strip():
            return

        try:
            conn = sqlite3.connect('weather_app.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE weather_data SET description=? WHERE id=?', (new_desc, id_to_update))
            conn.commit()
            conn.close()

            self.display_errors("Description updated successfully!")

        except sqlite3.Error as e:
            self.display_errors(f"DB Error: {e}")

    # delete data from DB
    def delete_record(self):
        id_to_delete, ok = QInputDialog.getInt(self, "Delete Record", "Enter Record ID:")
        if not ok:
            return

        try:
            conn = sqlite3.connect('weather_app.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM weather_data WHERE id=?', (id_to_delete,))
            conn.commit()
            conn.close()

            self.display_errors("Record deleted successfully!")

        except sqlite3.Error as e:
            self.display_errors(f"DB Error: {e}")

    # export data in csv, json
    def export_data(self):
        try:
            conn = sqlite3.connect('weather_app.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM weather_data")
            rows = cursor.fetchall()
            conn.close()

            # Export to JSON
            with open("weather_export.json", "w") as f_json:
                json.dump([{
                    "id": r[0],
                    "location": r[1],
                    "temperature": r[2],
                    "description": r[3],
                    "timestamp": r[4]
                } for r in rows], f_json, indent=4)

            # Export to CSV
            with open("weather_export.csv", "w", newline='') as f_csv:
                writer = csv.writer(f_csv)
                writer.writerow(["ID", "Location", "Temperature", "Description", "Timestamp"])
                writer.writerows(rows)

            self.display_errors("Exported to JSON and CSV successfully!")

        except Exception as e:
            self.display_errors(f"Export Error: {e}")



if __name__ == "__main__":          # if running directly create weather app object
    app = QApplication(sys.argv)    # send cmd line arguments to app
    weather_app = WeatherApp()
    weather_app.show()              # show our app
    sys.exit(app.exec_())           # handles events within our app

