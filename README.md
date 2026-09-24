# Notation d'un projet éolien — vue 3D

Application Streamlit : notation multicritère (environnemental / économique / social)
d'un projet éolien, avec visualisation 3D (rayon = note, hauteur = poids d'importance),
comparaison à un profil de référence, et export des résultats.

## Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Déploiement (GitHub + Streamlit Community Cloud)

1. Créez un dépôt GitHub (public ou privé) contenant `app.py` et `requirements.txt`.
2. Sur https://share.streamlit.io, connectez votre compte GitHub, choisissez le dépôt,
   la branche, et indiquez `app.py` comme fichier principal.
3. Cliquez sur « Deploy ». L'application sera accessible sur une URL du type
   `https://<nom-app>.streamlit.app`.

Toute mise à jour poussée sur la branche déployée redéploie automatiquement l'application.
