# BFUP armé – béton armé : applet de l'exemple 1

Applet Streamlit qui reproduit l'exemple 1 (§8, p. 38-40) du cours « Structures existantes – Examen et interventions » : dalle de roulement de pont (1969) renforcée par une couche de BFUP armé.

- **ELU (points 1-3)** : résistance de la dalle en béton armé seule m_R,0, résistance plastique de la section composée m_R,1, contrôle de la déformation du béton, vérification m_Rd = m_R,1/γ_M ≥ M_d.
- **ELS (point 4)** : analyse en section avec ε_U,ser imposé à la fibre supérieure du BFUP, axe neutre par itération, comparaison avec m_ser.
- **Étude paramétrique** : m_R,1, m_Rd et le moment ELS en fonction de h_U, f_Utk, de l'armature du BFUP, de f_ck ou de h_c, avec export CSV.

Toutes les entrées sont modifiables dans la barre latérale ; les valeurs par défaut sont celles de l'énoncé. Chaque tab affiche la section, les déformations, les contraintes, les forces internes et le tableau de calcul, avec export PNG des figures.

## Lancer localement

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Déployer sur Streamlit Community Cloud

1. Pousser ce dossier dans un dépôt GitHub (public ou privé).
2. Sur [share.streamlit.io](https://share.streamlit.io), se connecter avec GitHub, puis **Create app**.
3. Choisir le dépôt, la branche `main` et le fichier principal `app.py`, puis **Deploy**.

L'applet est redéployée automatiquement à chaque `git push`.

## Structure

| Fichier | Rôle |
|---|---|
| `app.py` | Interface Streamlit |
| `bfup_ex1.py` | Calculs (ELU, ELS) et fonctions de tracé ; utilisable seul dans Spyder |
| `test_app.py` | Tests : valeurs du corrigé et exécution de l'applet (`pytest`) |
| `requirements.txt` | Dépendances |
| `.streamlit/config.toml` | Thème |

## Écarts relevés dans le corrigé du cours

- Point 3 : le corrigé divise par 1.30 (→ 208.8 kNm/m) alors que l'énoncé donne γ_M = 1.20 (→ 226.4 kNm/m).
- Le gain « de presque 70 % » compare une valeur de dimensionnement à une valeur caractéristique ; en valeurs caractéristiques, le gain est de +120 %.
- Tableau ELS : A_s,ct est placé à d = 171 mm au lieu de 180 mm. Avec 180 mm : x = 81.3 mm, m = 139.2 kNm/m (corrigé : 80.5 mm, 134 kNm/m). L'option « Reproduire le tableau ELS du corrigé » applique 171 mm.

Unités internes : N, mm, MPa.
