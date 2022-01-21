
# cBot-Project

## Installation

Mise en place du projet:
`git clone https://github.com/CryptoRobotFr/cBot-Project.git`

Installation des dépendances:
`pip install -r requirements.txt`

Utilisation d'un environnement virtuel (recommandé):
`python -m venv .venv`
`.venv\Scripts\activate`
`pip install -r .\requirements.txt`

## Configuration

### Backtesting

Commencez par configurer la liste des paires sur lesquelles vous souhaitez travailler en copiant et renommant le fichier pair_list.json.dist en pair_list.json puis en le modifiant si besoin.

Depuis Vs code ou un autre IDE, téléchargez les données historiques avec les paramètres de votre choix en jouant le notebook Jupyter data_manager.ipynb

Vous pouvez désormais jouer les différents notebook de backtest présents dans le dossier backtest avec vos paramètres.

### Live

Commencez par configurer la liste des paires comme pour le backtest.

Faites de même avec le fichier config.json.dist à renommer en config.json et à renseigner avec vos clés API à destination de FTX.

Concerant la configuration des logs, il est possible d'utiliser 2 webhook discord.

Le premier webhook va afficher les logs à l'achat et à la vente au format :

>Sending BUY 0.3 of FTT/USD order at 46.489 price

Le 2eme permet de s'assurer que le bot à bien été lancé :

>Starting bot CBOT at 21-01 01:00:03

Pour de l'aide concernant la mise en place d'un webhook :

><https://support.discord.com/hc/fr/articles/228383668-Utiliser-les-Webhook>

Pour lancer concrètement le projet en live, je vous invite à regarder les différentes vidéos de [CryptoRobot](https://www.youtube.com/channel/UCGjfXO9kR34es5IsHLyP5eA) à ce sujet

## Crédits

Si vous souhaitez nous soutenir financièrement pour le développement des projets CryptoRobot voici une adresse de donation:

L'adresse ci dessous accepte les tokens type ERC20 sur les différentes blockchain Ethereum compatible (Ethereum - Binance Smart Chain(BSC) - Avax cChain - Polygon - Fantom - Cronos)

>0x6c1d1B9AaF0D6f7d5f4652f96024E1A42B316526
