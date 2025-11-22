/*
* Le script qui crée la structure de la base de données
*
* Fichier : init_bd.sql
* Auteur : Didier Mathieu
* Langage : SQL
* Date : 2025-11-12
*/
DROP DATABASE IF EXISTS pizzeria_2444332;
CREATE DATABASE pizzeria_2444332;

USE pizzeria_2444332;


/*******************************************************************************/
/************************* Création des tables *********************************/
/*******************************************************************************/


CREATE TABLE clients (
	id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    numero_telephone VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE commandes (
	id INT PRIMARY KEY AUTO_INCREMENT,
    id_client INT NOT NULL,
    date_commande DATETIME NOT NULL,
    date_livraison DATETIME,
	adresse VARCHAR (255) NOT NULL,
    FOREIGN KEY (id_client) REFERENCES clients (id)
);

CREATE TABLE croutes (
	id INT PRIMARY KEY AUTO_INCREMENT,
    type_croute VARCHAR(50) NOT NULL
);

CREATE TABLE sauces (
	id INT PRIMARY KEY AUTO_INCREMENT,
    nom_sauce VARCHAR(50) NOT NULL
);

CREATE TABLE garnitures (
	id INT PRIMARY KEY AUTO_INCREMENT,
    nom_garniture VARCHAR(100) NOT NULL
);

CREATE TABLE pizzas (
	id INT PRIMARY KEY AUTO_INCREMENT,
    id_commande INT NOT NULL,
    id_croute INT NOT NULL,
	id_sauce INT NOT NULL,
    FOREIGN KEY (id_commande) REFERENCES commandes(id),
    FOREIGN KEY (id_croute) REFERENCES croutes(id),
    FOREIGN KEY (id_sauce) REFERENCES sauces(id)
);

CREATE TABLE garnitures_pizzas (
	id_pizza INT NOT NULL,
    id_garniture INT NOT NULL,
    PRIMARY KEY(id_pizza, id_garniture),
    FOREIGN KEY (id_pizza) REFERENCES pizzas(id),
    FOREIGN KEY (id_garniture) REFERENCES garnitures(id)
);

CREATE TABLE attente_livraisons (
	id INT PRIMARY KEY AUTO_INCREMENT,
    id_commande INT NOT NULL,
    FOREIGN KEY (id_commande) REFERENCES commandes (id)
);


/*******************************************************************************/
/****************************  Triggers  ***************************************/
/*******************************************************************************/



DELIMITER $$
# Trigger pour ajouter les commandes automatiquement en attente livraison
CREATE TRIGGER commande_attente_livraison
    AFTER INSERT
    ON commandes FOR EACH ROW
    BEGIN
		INSERT INTO attente_livraisons (id_commande)
		VALUES (NEW.id);
    END $$
    
# Trigger pour ajouter la date de livraison quand on enleve de la table 
CREATE TRIGGER date_livraison_commande
    AFTER DELETE
    ON attente_livraisons FOR EACH ROW
    BEGIN
		UPDATE commandes
        SET date_livraison = NOW()
        WHERE id = OLD.id_commande;
    END $$

DELIMITER ;


/*******************************************************************************/
/**************************** Insertions ***************************************/
/*******************************************************************************/


INSERT INTO clients (nom, prenom, numero_telephone)
	VALUES 
		('Price', 'Carey', '999-999-9999');
        
INSERT INTO commandes (id_client, date_commande, adresse)
	VALUES 
		(1, now(), '12 Rue Dupré, Montréal, Québec');

INSERT INTO croutes (type_croute)
	VALUES 
		('Classique'),
		('Mince'),
        ('Épaisse');
        
INSERT INTO sauces (nom_sauce)
	VALUES 
		('Tomate'),
        ('Spaghetti'),
        ('Alfredo');
        
INSERT INTO garnitures (nom_garniture)
	VALUES
		('Pepperoni'),
        ('Champignons'),
        ('Oignons'),
        ('Poivrons'),
        ('Olives'),
        ('Anchois'),
        ('Bacon'),
        ('Poulet'),
        ('Maïs'),
        ('Fromage'),
        ('Piments forts');	
        #Pepperoni, Champignons, Oignons, Poivrons, Olives, Anchois, Bacon, Poulet, Maïs, Fromage, Piments forts
	
INSERT INTO pizzas (id_commande, id_croute, id_sauce)
	VALUES
		(1, 2, 2);
        
# PEPPERONI, OIGNONS, ANCHOIS
INSERT INTO garnitures_pizzas (id_pizza, id_garniture)
	VALUES
		(1,1),
        (1,3),
        (1,6);