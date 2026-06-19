# Gestion des environnements, notebooks et exécution (P07)

## 1. Définitions simples

### Notebook (.ipynb)
Un notebook est un fichier qui contient :
- du code Python
- du texte (explications)
- des résultats (graphes, tableaux)

Exemple :
1_modeling.ipynb

---

### Kernel
Un kernel = l’endroit où ton code s’exécute

Exemple :
- ton PC (VS Code)
- Google Colab

---

### Environnement Python
Un environnement = un espace avec :
- Python
- des librairies (pandas, sklearn…)

Exemple :
- environnement local VS Code
- environnement Colab

---

## 2. Organisation du projet

### Code (GitHub / Local)

- notebooks/
- src/
- api/
- tests/

👉 contient le code

---

### Données (Google Drive)

- data/raw/
- data/processed/

👉 contient les fichiers CSV

---

## 3. Workflow de travail

### Règle principale

GitHub = source de vérité

---

### Cas 1 : travail sur PC perso (VS Code)

Objectif :
- écrire le code
- structurer le notebook
- versionner

Étapes :

1. git pull
2. modifier le code
3. git add .
4. git commit -m "message"
5. git push

---

### Cas 2 : travail sur PC pro (Colab)

Objectif :
- exécuter le code
- entraînement modèle
- accès données

Étapes :

1. ouvrir notebook depuis GitHub
2. connecter Google Drive
3. exécuter le code
4. sauvegarder vers GitHub

---

## 4. Rôle de chaque outil

### VS Code
- écrire le code
- organiser le projet
- versionner avec Git

---

### Google Colab
- exécuter le code
- faire du machine learning
- accéder aux données

---

### GitHub
- stocker le code
- historiser les modifications
- synchroniser entre machines

---

## 5. Règles importantes

- Ne pas exécuter le code dans VS Code (au début)
- Toujours faire git pull avant de travailler
- Toujours commit régulièrement
- Ne jamais versionner les données
- Utiliser Colab pour les calculs

---

## 6. Résumé simple

VS Code → écrire  
Colab → exécuter  
GitHub → stocker  

``