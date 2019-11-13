# Labs-Python

Ce répertoire github comporte tous les projets Labs-Python, avec l’intégralité du code utilise et des bibliothèques mises en œuvre avec des commentaires et des explications du contenus utilisés.

Les scripts sont codee sur **PyCharm Professional 2019.2** avec l'interpréteur **Python 3.8 stable**.

   Vous pouvez télécharger :
        [PyCharm Professional Student](https://www.jetbrains.com/student/) / [Python 3.7]( https://www.python.org/ftp/python/3.7.0/python-3.7.0-amd64.exe)
        
Je rajouterais un tuto pour la config de l'interpréteur PyCharm

# Lab 1 – Intersection entre trajectoire et une porte

Ce Lab traite presque tous les aspects de python, et spécialement l’aspect ***POO (Programmation Orientée Objet)***.

## La POO
La programmation orientée objet (POO) permet de créer des entités (objets) que l'on peut manipuler . La programmation orientée objet impose des structures solides et claires. Les objets peuvent interagir entre eux, cela facilite grandement la compréhension du code et sa maintenance.

### La notion Classe et instanciation sur Python
Une classe regroupe des fonctions et des attributs qui définissent un objet. On appelle par ailleurs les fonctions d'une classe des " méthodes "

```python
# Pour créer une classe il suffit d'écrire 'class' suivi du nom de la classe
# Ici on a créé un classe Point

class Point:
  # Là je peux mettre les attributs de classe s'ils existent comme :
  # self.x = 23 (self qui permet d'appeler l'objet instancie 
  # et de lui assigner une valeur de 23
  
  # Si dans une classe on commence par 'def' on définit une méthode pour la classe
  # il est toujours obligatoire de définir une méthode __init__ qui initialisera l'instance
  def __init__(self, id_=None, date=None, x_=.0, y_=.0):
    self.id = id_
    self.date = date
    self.x = x_
    self.y = y_
```

## Les bibliothèques utilisées
Dans la Lab1 on a utilisé pas mal de bibliothèques, citons :

```python
import pandas as pd
import numpy as np
import csv
```

### Pandas a next level lib for data analysis
Pandas est une bibliothèque écrite pour le langage de programmation Python permettant la manipulation et l'analyse des données. Elle propose en particulier des structures de données et des opérations de manipulation de tableaux numériques et de séries temporelles.

#### Pandas DataFrame
Pandas permet de lire plusieurs types de base de donnees, ici on traite juste le traitement des fichiers ***.csv (Comma Separated Values)***

La syntaxe est assez simple:
```python
# On importe Pandas
import pandas as pd

# initialiser le dataframe
# df = pd.read_csv("chemain/vers/labase.csv", sep = le separateur entre valeur il peut etre ",/;/ "
df = pd.read_csv("data.csv", sep=";")
```

```python console
In[1] df = pd.read_csv("data.csv", sep=";")
```
On affiche la base:
```python console
In[2] df
Out[2]: 
       id              date          x        y
0      35  02/06/2019 15:00  47.254822 -2.36206
1       1  02/06/2019 15:30  47.247139 -2.36947
2      10  02/06/2019 15:30  47.251400 -2.36990
3      11  02/06/2019 15:30  47.220459 -2.38171
4      12  02/06/2019 15:30  47.250000 -2.37030
    ..               ...        ...      ...
62485   3  07/06/2019 14:00  48.377178 -4.48933
62486  15  07/06/2019 14:00  51.696751 -8.51682
62487  39  07/06/2019 14:05  51.695702 -8.51710
62488  39  07/06/2019 14:10  51.695702 -8.51710
62489  39  07/06/2019 14:15  51.696999 -8.51520
[62490 rows x 4 columns]
```

On a 5 colonnes plutot que 4, pandas toujours rajoute une colonne pour l'indexage *on l'utilisera apres pour se positionner sur une ligne*.

#### Pandas et le filtre data
Pandas possede lui aussi une methode **super** simple qui permet de filtrer dans une base de donnees

Reprenons le code precedent
```python
import pandas as pd

df = pd.read_csv('data.csv', sep=';')

# On doit d'abord selectionner sur quoi filtrer
# Dans notre cas on va filtrer par colonne et pour ceux on a deux methodes
# Methode 1 : Pointage direct ==> df.NomDeMaColonne / exp : df.id ou df.x ou df.y
# Methode 2 : Pointage par nom de colonne ==> df['NomDeMaColonne'] / exp : df['id']
# On utilisera la methode 2 dans notre script

# On cree un variable is_in
is_in = df['id'] == 1

# is_in va balayer toute la dataframe dans la colonne id
print(is_in)
```

```python console
Out[3]: 
0        False
1         True
2        False
3        False
4        False
         ...  
62485    False
62486    False
62487    False
62488    False
62489    False
```

Pour filtrer la table on utilisera la variable is_in
*On reprend toujours le code precedent*
```python
df_filtered = df[is_in]

print(df_filtered)
```

```python console
Out[4]: 
       id              date          x        y
1       1  02/06/2019 15:30  47.247139 -2.36947
47      1  02/06/2019 15:45  47.236980 -2.37721
92      1  02/06/2019 16:00  47.234219 -2.39391
139     1  02/06/2019 16:05  47.233780 -2.38284
211     1  02/06/2019 16:10  47.237160 -2.38670
    ..               ...        ...      ...
62202   1  07/06/2019 09:50  51.696201 -8.51664
62251   1  07/06/2019 10:00  51.696152 -8.51663
62318   1  07/06/2019 11:00  51.696152 -8.51665
62373   1  07/06/2019 12:00  51.696178 -8.51665
62442   1  07/06/2019 14:00  51.696171 -8.51661
```
Et la on a notre table filtree
Tout a l'heure je vous ai dis qu'on aura besoin de la premiere colonne d'indexage

pour prendre les valeurs de la table filtree, on utilise la methode `iloc` de la classe dataframe

```python
# On iterre d'abord sur les lignes de la base et on stock les indexages (la colonne 0) dans un vecteur
  for i in df_filtered.iterrows():
    indexes.append(i[0])

# On balaye notre vecteur d'indices et on a l'aide de la fonction iloc on se positionne sur la ligne
# Sans oublier le pointage sur la colonne desiree

  for i in indexes:
    x.append(df.iloc[i].x)
    y.append(df.iloc[i].y)
    
print(x)
print(y) 
```

```python console
[47.24713898,
 47.23698044,
 47.2342186,
 47.23377991,
 47.23715973,
 47.23563004,
 47.23147964,
 47.23160934,
 47.2279892,
 47.225341799999995,
 ...]
 
 [-2.369469881,
 -2.3772099019999997,
 -2.393909931,
 -2.382839918,
 -2.386699915,
 -2.391200066,
 -2.383949995,
 -2.383539915,
 -2.3947699069999997,
 ...]
 ```
 Et voila, on a obtenu nos vecteurs coordonnees x et y qu'on peut plotter apres.
 
 # Lab 2 - Un UI pour le Lab 1 *(Qt Designer - PyQt)*
