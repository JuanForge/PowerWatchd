# PowerWatchd

**Projet open source dédié à la gestion intelligente de l’alimentation des serveurs Linux fonctionnant 24/7.**

Il surveille l’état électrique et les UPS, détecte les coupures ou anomalies, et exécute automatiquement des actions planifiées pour protéger les services, éviter la corruption des données et garantir la continuité du système.

## Aperçu

PowerWatchd est un daemon léger pour **serveurs Linux (Debian 12 testé)**, conçu pour protéger les services lors de coupures UPS.  
Il communique avec systemd pour arrêter proprement les services selon l’état de la batterie de l’UPS et les dépendances entre services.

Caractéristiques principales :
- Spécialisé pour les UPS
- Détection des événements **OnBattery** via USB HID (NUT)
- Arrêts propres immédiats des services

## Fonctionnalités

- Détection des événements **OnBattery** sur l’UPS
- Exécution de **séquences d’arrêt de services prédéfinies** avec respect des dépendances
- Seuils basés sur **le pourcentage de batterie restante** pour déclencher les arrêts
- Totalement automatisé, **aucune interface CLI ou web nécessaire**
- Fonctionne comme un **service systemd**

## Backend
- 0 : Stable et testé depuis longtemps
- 1 : En test : fonctionne mais pas encore stabilisé
- 2 : Dernière version expérimentale : très rapide, faible consommation de ressources
- valeur par defaut : 2

## Update
Modification du code permettant de réduire la charge sur le réseau (puisque moins besoin de requêtes du client pour l'actualisation), tout en offrant un temps de réactivité réduit pour signaler un changement sur le serveur vers le client.