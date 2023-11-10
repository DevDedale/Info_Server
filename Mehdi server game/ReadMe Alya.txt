
Travail fait avec Alya Amarsy en Mars 2023:

But: les joueurs portent une smart watch avec leur score, leur état Chevalier D'Or et le Chrono du jeu.
Le GameMaster peut changer ces valeurs sur son interface (sur un téléphone)

- - - - - - - - - - - - - - - 
Fonctionnement:
- - - - - - - - - - - - - - - 

- - - - - - - - - - - - - - - 

Un serveur (en python, utilisant SocketIO) est le GameServer.
Il crée la partie et envoie régulièremnt l'état de celle-ci.


Pour le lancer, il faut faire  GameServer:     Python ServerMain.py
Ce server est sur le port 5000

- - - - - - - - - - - - - - - 
Le client GameMasterTablet (développé sous Unity par Patrick) récupère l'état du serveur et l'affiche à l'écran (6 joueurs + salle courante) et donne la possibilité de changer les valeurs  par des commandes auprès du ServerMain.

- - - - - - - - - - - - - - - 
Le Server Dedale-watches---alternate-server (développé par Alya) est un server utilisant Flask , développé en python. "app.py".  pour le lancer il faut lancer:
flask run --host=0.0.0.0 --port=5002

Ce server est visible dans Firefox  (localhost:5002)
On y voit les Games répertoriés.
Il y a une manip qui ne peut être faite qu'ici: associer les adresses Mac des montres à un jeu et à un rôle
Pour voir une montre, il faut que son client ait été lancé.
Elle apparaît alors automatiquement dans la liste.


- - - - - - - - - - - - - - - 
Le client des montres est dans le dossier "Alya".
Il faut l'ouvrir avec Visual Studio Code
(plusieurs librairies à installer dont platformio -> demander à Alya)
Dna sle ba de Studio Code on voit une barre bleu "platformio"
La flèche -> permet de lancer l'app sur la montre branchée sur le PC

La montre affiche alors le score du personnage qui lui a été affecté.

- - - - - - - - - - - - - - - 
TODO pour que ça marche
- - - - - - - - - - - - - - - 
Vérifier les ports GameServer (5000) et AlternateServer (5001)

Dans le code Alya/main.cpp ligne 36, indiquer l'adresse IP de l'AlternateServer  (192.168.1.23 chez moi, 192.168.1.141 au dédale) et son port

Dans le code Alya/main.cpp ligne 32, indiquer le nom du Wifi et son mot de passe.


Dans le code GameMasterTablet, sous Unity.
Il faut aller dans la Hierarchy, cliquer sur CubeCommunicator.
Dans son Inspector, on trouve le component Socket.IO Comunicator.
le champ SocketIO Adress doit contenir 192.168.1.141:5000  soit l'adresse du GameServer

Dnas le code de l'AlternateServer, app.py, ligne 19, il y a l'adresse  de GameServer à changer si nécessaire : sio.connect("ws://192.168.1.23:5000")


- - - - - - - - - - - - - - - 
NOTES Importantes
- - - - - - - - - - - - - - - 
Le téléphone doit être en Developper Mode pour pouvoir être chargé par Unity.

Il doit avoir le Wifi pour fonctionner.

noter les adresses mac des montres

- - - - - - - - - - - - - - - 
Charger les montres!

- - - - - - - - - - - - - - - 
A l'heure actuelle, le seul jeu créé est le jeu numéro 8.
Cette semaine il faut clarifier la boucle de création des jeux.
Elle doit démarrer depuis le GameMaster, réceptionné par GameServer et communiqué à AlternateServer
