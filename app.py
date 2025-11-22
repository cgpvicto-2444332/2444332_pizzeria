import os
from dotenv import load_dotenv
import mysql.connector
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
from mysql.connector import Error

app = Flask(__name__)

load_dotenv()

# Récupère les variables d'environnement du .env
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT')

# Configuration de la connexion à la base de données
def db_config():
    """Cette fonction permet de se connecter à la base de données."""
    try:
        db = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        port=db_port
        )
        return db
    except Error as e:
        print(f"Oups, erreur de connexion à la base de données: {e}")
        return None

@app.route('/api/client/<int:client_id>')
def get_client(client_id):
    """
    Récupère les informations d'un client par son identifiant.

    Cette fonction établit une connexion à la base de données, exécute une
    requête pour sélectionner les informations du client (nom, prénom, numéro de
    téléphone) dans la table 'clients' correspondant à l'identifiant fourni.
    Si le client est trouvé, ses données sont renvoyées.
    En cas d'erreur de connexion à la base de données, d'identifiant inconnu
    (client non trouvé), ou d'erreur SQL, un message d'erreur approprié est renvoyé.

    Args:
        client_id (int): L'identifiant du client à récupérer.

    Returns:
        Les données du client en format JSON si succès,
        ou un message d'erreur si échec.
    """
    db = db_config()
    if db is None:
        return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
        
    cursor = db.cursor(dictionary=True)
    try:
        # Récupérer les informations du client avec son ID fournit dans la BD
        cursor.execute("SELECT id, nom, prenom, numero_telephone FROM clients WHERE id = %s", (client_id,))
        client = cursor.fetchone()
        
        if client:
            return jsonify(client)
        else:
            return jsonify({'error': 'Client non trouvé'}), 404
    except Error as e:
        print(f"Oups, erreur avec la requête SQL: {e}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

@app.route('/')
def index():
    """
    Affiche la page d'accueil de la pizzeria et récupère les ingrédients disponibles.

    Cette fonction établit une connexion à la base de données, exécute une
    requête pour sélectionner les informations des croutes, sauces et 
    garnitures dans les tables 'croutes', 'sauces' et 'garnitures'.
    Une fois les données récupérées, elle ferme la connexion et affiche
    la page d'index (formulaire) et lui fournie les données pris dans les requêtes.

    Args:
        Aucun

    Returns:
        Le template HTML 'index.html' avec les listes de croûtes,
        sauces et garnitures pour la sélection de l'utilisateur,
        ou un message d'erreur si échec.
    """
    # Connexion à la base de données
    db = db_config()
    if db is None:
        return "Erreur: Impossible de se connecter à la base de données.", 500
    
    # Création d'un cursor pour effectuer les requêtes sql
    cursor = db.cursor()
    
    try:
        # Récupérer les croûtes dans la BD
        cursor.execute("SELECT id, type_croute FROM croutes")
        croutes = cursor.fetchall()
        
        # Récupérer les sauces dans la BD
        cursor.execute("SELECT id, nom_sauce FROM sauces")
        sauces = cursor.fetchall()
        
        # Récupérer les garnitures dans la BD
        cursor.execute("SELECT id, nom_garniture FROM garnitures")
        garnitures = cursor.fetchall()
            
        # Afficher la page d'index et fournie les données de la BD
        return render_template('index.html', croutes=croutes, sauces=sauces, garnitures=garnitures)
    except Error as e:
        # Affiche un message d'erreur si une erreur occure
        print(f"Erreur SQL lors de l'initialisation de la page: {e}")
        return "Erreur lors de la récupération des ingrédients.", 500
    finally:
        # Ferme la connexion à la base de données et le cursor
        if cursor:
            cursor.close()
        if db:
            db.close()

@app.route('/confirmation', methods=['POST'])
def confirmation():
    """
    Traite la commande de pizza soumise et affiche une page de confirmation de commande.

    Cette fonction reçoit les données d'une commande via une requête POST. 
    Elle se connecte à la base de données pour récupérer les noms croûtes, 
    de la sauce et des garnitures à partir de leurs identifiants. 
    Elle assemble ensuite le résumé complet de la commande pour 
    l'afficher sur la page 'confirmation.html'.
    En cas d'erreur de connexion à la base de données, ou d'erreur SQL, 
    un message d'erreur approprié est renvoyé.

    Args:
        Aucun

    Returns:
        Le template HTML 'confirmation.html' affiché avec le résumé de la commande,
        ou un message d'erreur si échec.
    """
    db = db_config()
    if db is None:
        return "Erreur: Impossible de se connecter à la base de données.", 500
    
    # Récupérer les données du formulaire
    nom = request.form['nom']
    prenom = request.form['prenom']
    telephone = request.form['telephone']
    adresse = request.form['adresse']
    croute_id = request.form['croute']
    sauce_id = request.form['sauce']
    
    # Récupérer les garnitures (avec .get() pour éviter les erreurs si le champ est absent)
    garniture1 = request.form.get('garniture1', '')
    garniture2 = request.form.get('garniture2', '')
    garniture3 = request.form.get('garniture3', '')
    garniture4 = request.form.get('garniture4', '')
    garnitures_ids = [g for g in [garniture1, garniture2, garniture3, garniture4] if g]
    
    cursor = db.cursor()
    try:
        # Récupérer le nom de la croûte depuis la base de données en fonction du ID du formulaire (value)
        sql_croute = "SELECT type_croute FROM croutes WHERE id = %s"
        cursor.execute(sql_croute, (croute_id,))
        croute_result = cursor.fetchone()
        croute_nom = croute_result[0] if croute_result else "Non trouvée"
        
        # Récupérer le nom de la sauce depuis la base de données en fonction du ID du formulaire (value)
        sql_sauce = "SELECT nom_sauce FROM sauces WHERE id = %s"
        cursor.execute(sql_sauce, (sauce_id,))
        sauce_result = cursor.fetchone()
        sauce_nom = sauce_result[0] if sauce_result else "Non trouvée"
        
        # Récupérer les noms des garnitures depuis la base de données en fonction du ID du formulaire (value)
        # Section de code sur les garnitures pris sur (https://gemini.google.com/)
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
    except Error as e:
        print(f"Erreur SQL lors de la confirmation: {e}")
        return "Erreur lors de la vérification des ingrédients.", 500
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
    
    # Préparer les données de la commande pour l'affichage de confirmation
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
    """
    Enregistre une nouvelle commande de pizza dans la base de données.

    Cette fonction reçoit les données complètes d'une commande via une requête POST
    et les insère dans les tables de la base de données (clients, commandes, pizzas, garnitures_pizzas).
    Elle vérifie si le client existe déjà. Si oui, elle utilise son id existant. 
    Sinon, elle l'insère dans la table clients.
    Ensuite, elle insère la date du jour, l'adresse et le id de client dans commandes.
    Elle insère dans pizza le id de commande, le id de croute et de sauce.
    Finalement, elle insère dans garnitures_pizzas le id de la pizza et des garnitures.
    Elle redirige l'utilisateur vers la page de formualire après succès.
    En cas d'erreur de connexion à la base de données, ou d'erreur SQL, 
    un message d'erreur approprié est renvoyé.

    Args:
        Aucun

    Returns:
        Une redirection vers la fonction index() après une commande réussie,
        ou un message d'erreur si échec.
    """
    db = db_config()
    if db is None:
        return "Erreur: Impossible de se connecter à la base de données.", 500
    
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        telephone = request.form['telephone']
        adresse = request.form['adresse']
        croute = request.form['croute']
        sauce = request.form['sauce']
        
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
            sqlCheck = "SELECT id FROM clients WHERE (nom = %s AND prenom = %s)"
            cursor.execute(sqlCheck, (nom, prenom))
            client_existant = cursor.fetchone()

            if client_existant:
                client_id = client_existant[0]
            else:
                # Insérer le nouveau client
                sqlClient = "INSERT INTO clients (nom, prenom, numero_telephone) VALUES (%s, %s, %s)"
                values = (nom, prenom, telephone)
                cursor.execute(sqlClient, values)
                db.commit()
                # Note le id du client
                client_id = cursor.lastrowid
            
            date_commande = datetime.now()

            # Insérer la date, adresse et id_client dans commandes
            sqlCommande = "INSERT INTO commandes (id_client, date_commande, adresse) VALUES (%s, %s, %s)"
            values = (client_id, date_commande, adresse)

            cursor.execute(sqlCommande, values)
            # Note le id de la commande
            commande_id = cursor.lastrowid

            # Insérer le id de la commande, le id de la croute et le id de la sauce dans pizzas
            sqlPizza = "INSERT INTO pizzas (id_commande, id_croute, id_sauce) VALUES (%s, %s, %s)"
            values = (commande_id, croute, sauce)

            cursor.execute(sqlPizza, values)
            pizza_id = cursor.lastrowid

            # Insérer les garnitures dépendant du nombre
            if garnitures:
                sqlGarnitures = "INSERT INTO garnitures_pizzas (id_pizza, id_garniture) VALUES (%s, %s)"
                values_garnitures = [(pizza_id, g) for g in garnitures]
                cursor.executemany(sqlGarnitures, values_garnitures)
            
            # Commit une seule fois à la fin
            db.commit()
        except Error as e:
            db.rollback()
            print(f"Erreur inattendue : {e}")
            return "Une erreur inattendue est survenue.", 500
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    # Retourne la fonction de l'index
    return redirect(url_for('index'))

@app.route('/commandes_en_attente')
def commandes_en_attente():
    """
    Affiche la liste des commandes en attente de livraison.

    Cette fonction se connecte à la base de données pour récupérer tous les détails importants
    (le client, la pizza, les ingrédients) des commandes présentes dans la table
    'attente_livraisons'. Elle affiche ensuite ces informations via le template
    'commandes-en-attente.html'.
    Une fois les données récupérées, elle ferme la connexion et affiche
    la page listant les commandes et lui fournie les données pris dans les requêtes.

    Args:
        Aucun

    Returns:
        <La page listant les commandes en attente.
    """
    db = db_config()
    cursor = db.cursor()
    commandes = []
    
    try:
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
    
    except Error as e:
        print(f"Erreur SQL lors de la récupération des commandes en attente: {e}")
        return "Erreur lors de la récupération des commandes.", 500
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
    
    return render_template('commandes-en-attente.html', commandes=commandes)

@app.route('/livrer/<int:commande_id>', methods=['POST'])
def livrer(commande_id):
    """
    Retire une commande de la liste des livraisons en attente.

    Cette fonction supprime la commande (spécifiée par son identifiant) de la table
    'attente_livraisons' et redirige vers la liste des commandes à jour.
    En cas d'erreur de connexion à la base de données, ou d'erreur SQL, 
    un message d'erreur approprié est renvoyé.

    Args:
        commande_id (int): L'id de la commande livrée.

    Returns:
        Une redirection vers la fonction commandes_en_attente() après une supression réussie,
        ou un message d'erreur si échec.
    """
    db = db_config()
    cursor = db.cursor()
    
    try:
        sql = "DELETE FROM attente_livraisons WHERE id_commande = %s"
        cursor.execute(sql, (commande_id,))
        db.commit()
        
        # Rediriger vers la page des commandes en attente
        # Redirect pour faire afficher la page actualisée et non le template
        return redirect(url_for('commandes_en_attente'))
    except Exception as e:
        db.rollback()
        print(f"Erreur inattendue lors de la livraison : {e}")
        return "Une erreur inattendue est survenue.", 500
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

if __name__ == '__main__':
    app.run(debug=True)