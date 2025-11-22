import os
from dotenv import load_dotenv
import mysql.connector
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
from mysql.connector import Error

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

@app.route('/api/client/<int:client_id>')
def get_client(client_id):
    db = db_config()
    if db is None:
        return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
        
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nom, prenom, numero_telephone FROM clients WHERE id = %s", (client_id,))
        client = cursor.fetchone()
        
        if client:
            return jsonify(client)
        else:
            return jsonify({'error': 'Client non trouvée'}), 404
    except Error as e:
        print(f"Oups, erreur avec la requête SQL: {e}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500
    finally:
        cursor.close()
        db.close()

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

@app.route('/confirmation', methods=['POST'])
def confirmation():
    # Connexion à la base de données
    db = db_config()
    
    # Récupérer les données du formulaire
    nom = request.form['nom']
    prenom = request.form['prenom']
    telephone = request.form['telephone']
    adresse = request.form['adresse']
    croute_id = request.form['croute']
    sauce_id = request.form['sauce']
    
    # Récupérer les garnitures sélectionnées
    garniture1 = request.form.get('garniture1', '')
    garniture2 = request.form.get('garniture2', '')
    garniture3 = request.form.get('garniture3', '')
    garniture4 = request.form.get('garniture4', '')
    garnitures_ids = [g for g in [garniture1, garniture2, garniture3, garniture4] if g]
    
    # Récupérer le nom de la croûte depuis la base de données
    cursor = db.cursor()
    sql_croute = "SELECT type_croute FROM croutes WHERE id = %s"
    cursor.execute(sql_croute, (croute_id,))
    croute_result = cursor.fetchone()
    croute_nom = croute_result[0] if croute_result else "Non trouvée"
    cursor.close()
    
    # Récupérer le nom de la sauce depuis la base de données
    cursor = db.cursor()
    sql_sauce = "SELECT nom_sauce FROM sauces WHERE id = %s"
    cursor.execute(sql_sauce, (sauce_id,))
    sauce_result = cursor.fetchone()
    sauce_nom = sauce_result[0] if sauce_result else "Non trouvée"
    cursor.close()
    
    # Récupérer les noms des garnitures depuis la base de données
    cursor = db.cursor()
    garnitures_details = []
    for garniture_id in garnitures_ids:
        if garniture_id:
            sql_garniture = "SELECT nom_garniture FROM garnitures WHERE id = %s"
            cursor.execute(sql_garniture, (garniture_id,))
            
            garniture_resultat = cursor.fetchone()
            
            if garniture_resultat:
                nom_garniture = garniture_resultat[0]
                
                garnitures_details.append({
                    'id': garniture_id,
                    'nom': nom_garniture
                })
    cursor.close()
    
    # Fermeture du curseur et de la connexion
    db.close()
    
    # Préparer les données de la commande pour l'affichage
    commande_details = {
        'nom': nom,
        'prenom': prenom,
        'telephone': telephone,
        'adresse': adresse,
        'croute': {'id': croute_id, 'nom': croute_nom},
        'sauce': {'id': sauce_id, 'nom': sauce_nom},
        'garnitures': garnitures_details
    }
    
    # Afficher la page de confirmation avec les données
    return render_template('confirmation.html', commande=commande_details)


@app.route('/commander', methods=['POST'])
def commander():
    db = db_config()
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form['nom']
        prenom = request.form['prenom']
        telephone = request.form['telephone']
        adresse = request.form['adresse']
        croute = request.form['croute']
        sauce = request.form['sauce']
        
        # Récupérer les garnitures (avec .get() pour éviter les erreurs si le champ est absent)
        garniture1 = request.form.get('garniture1', '')
        garniture2 = request.form.get('garniture2', '')
        garniture3 = request.form.get('garniture3', '')
        garniture4 = request.form.get('garniture4', '')

        # Créer la liste des garnitures et filtrer les valeurs vides
        garnitures = [g for g in [garniture1, garniture2, garniture3, garniture4] if g]
        
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

            sqlCommande = "INSERT INTO commandes (id_client, date_commande, adresse) VALUES (%s, %s, %s)"
            values = (client_id, date_commande, adresse)

            cursor.execute(sqlCommande, values)
            db.commit()
            commande_id = cursor.lastrowid

            sqlPizza = "INSERT INTO pizzas (id_commande, id_croute, id_sauce) VALUES (%s, %s, %s)"
            values = (commande_id, croute, sauce)

            cursor.execute(sqlPizza, values)
            db.commit()
            pizza_id = cursor.lastrowid

            if garnitures:
                sqlGarnitures = "INSERT INTO garnitures_pizzas (id_pizza, id_garniture) VALUES (%s, %s)"
                values_garnitures = [(pizza_id, g) for g in garnitures]
                cursor.executemany(sqlGarnitures, values_garnitures)
            
            # Commit une seule fois à la fin
            db.commit()
            
        except mysql.connector.Error as err:
            db.rollback()  # Annuler en cas d'erreur
            cursor.close()
            return f"Erreur lors de l'insertion : {err}", 500
        
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    return redirect(url_for('index'))

@app.route('/commandes_en_attente')
def commandes_en_attente():
    db = db_config()
    cursor = db.cursor()
    
    # Requête pour récupérer toutes les commandes avec les détails (les 3 guillemets pour pas avoir a tout mettre sa meme ligne)
    sql = """
        SELECT 
            cmd.id,
            cmd.date_commande,
            cmd.adresse,
            cl.nom,
            cl.prenom,
            cl.numero_telephone,
            cr.type_croute,
            s.nom_sauce,
            GROUP_CONCAT(g.nom_garniture SEPARATOR ', ') as garnitures
        FROM attente_livraisons al
        JOIN commandes cmd ON al.id_commande = cmd.id
        JOIN clients cl ON cmd.id_client = cl.id
        JOIN pizzas p ON p.id_commande = cmd.id
        JOIN croutes cr ON p.id_croute = cr.id
        JOIN sauces s ON p.id_sauce = s.id
        LEFT JOIN garnitures_pizzas gp ON gp.id_pizza = p.id
        LEFT JOIN garnitures g ON gp.id_garniture = g.id
        GROUP BY cmd.id, cmd.date_commande, cmd.adresse, cl.nom, cl.prenom, cl.numero_telephone, cr.type_croute, s.nom_sauce
        ORDER BY cmd.date_commande
    """
    
    cursor.execute(sql)
    commandes = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return render_template('commandes-en-attente.html', commandes=commandes)

@app.route('/livrer/<int:commande_id>', methods=['POST'])
def livrer(commande_id):
    db = db_config()
    cursor = db.cursor()
    
    try:
        sql = "DELETE FROM attente_livraisons WHERE id_commande = %s"
        cursor.execute(sql, (commande_id,))
        db.commit()
        
        cursor.close()
        db.close()
        
        # Rediriger vers la page des commandes en attente
        # redirect pour faire afficher la page et non le template
        return redirect(url_for('commandes_en_attente'))
        
    except mysql.connector.Error as err:
        db.rollback()
        cursor.close()
        db.close()
        return f"Erreur lors de la livraison : {err}", 500
    
    finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

if __name__ == '__main__':
    app.run(debug=True)