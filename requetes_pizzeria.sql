use pizzeria;
select * from clients;
select * from commandes;
select * from pizzas;
SELECT * FROM garnitures;
SELECT * FROM croutes;
SELECT * FROM sauces;

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
FROM commandes cmd
JOIN clients cl ON cmd.id_client = cl.id
JOIN pizzas p ON p.id_commande = cmd.id
JOIN croutes cr ON p.id_croute = cr.id
JOIN sauces s ON p.id_sauce = s.id
LEFT JOIN garnitures_pizzas gp ON gp.id_pizza = p.id
LEFT JOIN garnitures g ON gp.id_garniture = g.id
GROUP BY cmd.id, cmd.date_commande, cmd.adresse, cl.nom, cl.prenom, cl.numero_telephone, cr.type_croute, s.nom_sauce
ORDER BY cmd.date_commande DESC