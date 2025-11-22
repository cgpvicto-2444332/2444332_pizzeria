Projet long de bd2
Auteur: Didier Mathieu
DA: 2444332
Date: 24 Novembre 2025
Commandes: 
    git clone https://github.com/TousignantSimon-BD2/remise-flask-cgpvicto-2444332/tree/main
    python -m venv myenv 
        Linux: source ./myenv/bin/activate
        Windows: .\myenv\Scripts\activate
    pip install -r requirements.txt
    mysql -u root -p database_pizza < ./scripts/init_bd.sql
    python app.py