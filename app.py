import os
from dotenv import load_dotenv
import mysql.connector
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

load_dotenv()

# Récupère les variables d'environnement
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT')

# Configuration de la connexion à la base de données
def db_config():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        port=db_port
)

@app.route('/')
def index():
    db = db_config()
    cursor = db.cursor()
    
    # Récupérer les croûtes
    cursor.execute("SELECT id, type_croute FROM croutes")
    croutes = cursor.fetchall()
    
    # Récupérer les sauces
    cursor.execute("SELECT id, nom_sauce FROM sauces")
    sauces = cursor.fetchall()
    
    # Récupérer les garnitures
    cursor.execute("SELECT id, nom_garniture FROM garnitures")
    garnitures = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return render_template('index.html', croutes=croutes, sauces=sauces, garnitures=garnitures)

@app.route('/commander', methods=['POST'])
def commander():
    db = db_config()
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form['nom']
        prenom = request.form['prenom']
        telephone = request.form['telephone']
        adresse = request.form['adresse']
        
        # Créer un curseur
        cursor = db.cursor()
        
        try:
            # Vérifier si le client existe déjà (nom + prénom)
            sqlCheck = "SELECT id FROM clients WHERE (nom = %s AND prenom = %s) OR numero_telephone = %s"
            cursor.execute(sqlCheck, (nom, prenom, telephone))
            client_existant = cursor.fetchone()

            if client_existant:
                client_id = client_existant[0]
            else:
                # Insérer le nouveau client
                sqlClient = "INSERT INTO clients (nom, prenom, numero_telephone) VALUES (%s, %s, %s)"
                values = (nom, prenom, telephone)
                cursor.execute(sqlClient, values)
                db.commit()
                client_id = cursor.lastrowid
            
            date_commande = datetime.now()
            sqlCommandes = "INSERT INTO commandes (id_client, date_commande, adresse) VALUES (%s, %s, %s)"
            values = (client_id, date_commande, adresse)
            cursor.execute(sqlCommandes, values)
            db.commit()
            commande_id = cursor.lastrowid
            
        except mysql.connector.Error as err:
            db.rollback()  # Annuler en cas d'erreur
            cursor.close()
            return f"Erreur lors de l'insertion : {err}", 500
        
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()
    
    # Si GET, afficher le formulaire
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)