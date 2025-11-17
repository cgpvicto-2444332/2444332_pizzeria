/*
* Le script qui crée la structure de la base de données
*
* Fichier : MathieuDidier_pizzeria.sql
* Auteur : Didier Mathieu
* Langage : SQL
* Date : 2025-11-12
*/
DROP DATABASE IF EXISTS pizzeria;
CREATE DATABASE pizzeria;

USE pizzeria;

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
/**************************** Insertions ***************************************/
/*******************************************************************************/



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
	