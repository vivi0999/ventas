
import mysql.connector
conexion=mysql.connector.connect(
    host="bifh5d2wnnbinrzkv8de-mysql.services.clever-cloud.com",
    user="uk3v9k2zh9qkjlg7",
    password="nnrdJpFcrhMR2xO8WNSj",
    database="bifh5d2wnnbinrzkv8de"
)
if conexion.is_connected():
    print("conexion")