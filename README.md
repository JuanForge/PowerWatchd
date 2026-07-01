# PowerWatchd

### This tool is actively maintained. Although updates may not be frequent, this is intentional: development prioritizes stability, reliability, and long-term correctness rather than continuous feature addition. It is personally used to validate its robustness in real usage scenarios.

### Make sure to download the releases, not the main branch.

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
- **Prometheus** integration support with ```--prometheus```

## Backend
- 0 : Stable et testé depuis longtemps
- 1 : En test : fonctionne mais pas encore stabilisé
- 2 : Dernière version expérimentale : très rapide, faible consommation de ressources
- valeur par defaut : 2

# INFO
When the client runs on the same host as the server, the shutdown threshold must be adjusted to avoid race conditions during coordinated shutdown.
If all components share the same threshold, the master node may terminate before propagating shutdown signals to its clients.

Therefore, the master server should use a lower threshold than its clients (e.g., 20% for the master vs 25% for clients) to guarantee proper shutdown sequencing.

## Python
python3.12.3