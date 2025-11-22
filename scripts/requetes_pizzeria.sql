/*
* Un script test qui vérifie la présence de données dans les tables
* et dans lequel je peux expérimenter des select pour l'appli FLASK
*
* Fichier : requetes_pizzeria.sql
* Auteur : Didier Mathieu
* Langage : SQL
* Date : 2025-11-12
*/

use pizzeria_2444332;
select * from clients;
select * from commandes;
select * from pizzas;
SELECT * FROM garnitures;
SELECT * FROM croutes;
SELECT * FROM sauces;
select * from attente_livraisons;

DELETE FROM attente_livraisons WHERE id_commande = 2;

# Requête qui affiche toutes les informations nécessaires pour vérification
SELECT 
	cl.id AS id_client,
    p.id AS id_pizza,
    p.id_commande,
    com.adresse,
    cl.nom,
    cl.prenom,
    cl.numero_telephone,
    c.type_croute,
    s.nom_sauce,
    GROUP_CONCAT(g.nom_garniture SEPARATOR ', ') AS garnitures, # Pour afficher les noms de garnitures sur la même ligne
    com.date_commande,
    com.date_livraison
FROM pizzas p
INNER JOIN garnitures_pizzas gp ON gp.id_pizza = p.id
INNER JOIN garnitures g ON g.id = gp.id_garniture
INNER JOIN croutes c ON c.id = p.id_croute
INNER JOIN sauces s ON s.id = p.id_sauce
INNER JOIN commandes com ON com.id = p.id_commande
INNER JOIN clients cl ON cl.id = com.id_client
GROUP BY p.id, p.id_commande, com.adresse, cl.nom, cl.prenom, cl.numero_telephone, c.type_croute, s.nom_sauce;


# Requete simplifiée pour l'appli flask
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
LEFT JOIN garnitures_pizzas gp ON gp.id_pizza = p.id # Left join pour les pizzas sans garnitures
LEFT JOIN garnitures g ON gp.id_garniture = g.id
GROUP BY cmd.id, cmd.date_commande, cmd.adresse, cl.nom, cl.prenom, cl.numero_telephone, cr.type_croute, s.nom_sauce
ORDER BY cmd.date_commande