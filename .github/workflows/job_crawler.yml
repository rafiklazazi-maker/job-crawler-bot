name: Job Crawler Auto Notifier

on:
  schedule:
    # Les heures UTC correspondant à 8h, 10h, 13h et 15h (Heure d'Algérie / UTC+1)
    - cron: '0 7,9,12,14 * * *'
  workflow_dispatch: # Permet aussi de lancer le scan manuellement depuis GitHub si besoin

jobs:
  run-crawler:
    runs-on: ubuntu-latest

    steps:
    - name: Récupérer le code du dépôt
      uses: actions/checkout@v3

    - name: Configurer Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Installer les dépendances
      run: |
        python -m pip install --upgrade pip
        pip install requests beautifulsoup4

    - name: Exécuter le Job Crawler
      run: python job_crawler_cron.py