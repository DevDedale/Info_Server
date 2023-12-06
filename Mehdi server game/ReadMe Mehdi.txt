Lancer MobaXTerm pour avoir une console sur le PC de Mehdi

mon password global est:
P... pour mobaxterm
loutre
I....


sinon le pass noté sur un carton


pour lancer le server, aller dans:
/opt/magichanism/scenarios/dedale

pour info, en cas de pb,
docker-compose up -d   
démarre la list des dockers qui sont dans docker-compose.yml
(fait automatiquement quand on démarre le server)


docker-compose ps  
Voir la liste des servers

        Name                      Command               State                    Ports
--------------------------------------------------------------------------------------------------------
dedale_dns_1           dnsmasq -k                       Up      53/tcp, 0.0.0.0:53->53/udp
dedale_game-server_1   mgi-game-server-docker-ent ...   Up
dedale_mosquitto_1     /docker-entrypoint.sh /usr ...   Up      0.0.0.0:1883->1883/tcp
dedale_nginx_1         /docker-entrypoint.sh ngin ...   Up      0.0.0.0:443->443/tcp, 0.0.0.0:80->80/tcp



docker-compose logs --tail=100 -f game-server
voir les erreurs

docker-compose restart game-server
relancer le server


si on a trop de messages
on peut relancer le docker:
docker-compose down
docker-compose up -d


- - - - - - - - - - -

Pour lancer les servers de Pat,
aller dans /opt/magichacanism/scenarios/testMars
cd ..
ls

puis dans GameServer
python3 ServerMain.py

dans Dedale..alternate
flask run --host=0.0.0.0 --port=5002


ouvrir sur firefox
http://10.65.0.200:5002/
pour voir le server alternate de Alya



- - - - - --  -  --- -

Interface de Mehdi

https://server.dedale.local.magichanism.com/
http://server.dedale.local.magichanism.com/




- - - - - - - - - - -- - 
mosquitto_sub -h 10.65.0.200 -t '#' -v 
pour écouter les messages mqtt
où 10.65.0.200  = IP du serveur magichanism


- - - - - - - - - - - - - - - - - - 
mosquitto_sub -h 10.65.0.200 -t '#' -v | grep groom
mosquitto_sub -h 10.65.0.200 -t '#' -v | grep connected
pour voir les adresses des appareils sur le reseau

mosquitto_sub -h 10.65.0.200 -t '#' -v | grep dmx

mosquitto_sub -h 10.65.0.200 -t '#' -v | grep answer
mosquitto_pub -h 10.65.0.200 -t mytopic/test -m "mon message"
mosquitto_pub -h 10.65.0.200 -t mytopic/test -m '"mon message"'   //message en JSon



