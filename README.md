# Analyse Belisama
Cadre d'analyse pour Belisama en Python

- Version : 1.0
- Dernière mise à jour : 20 août 2020
- Auteur : Yuuki Wada

## Introduction
Belisama est un projet de mesure des radiations pendant les orages en France. Ce projet est mené par l'Université de Paris/APC, l'Université d'Orléans/LPC2E, l'Université de Bourgogne, l'IRSN, le CEA/IRFU, le CNES, le CNRS/IN2P3, le Labex UnivEarth, le CSNSM, la Société d'Astronomie de Bourgogne, l'Université de Nagoya, et RIKEN. [Le site du projet est ici.] (https://ikhone.wixsite.com/belisama)

L'instrument de mesure des rayonnements fournit une liste des photons gamma détectés : le temps et son énergie sous forme de FITS (système flexible de transport d'images), qui est souvent utilisé pour l'astronomie, l'astrophysique, les sciences de la terre et de l'espace. Ce cadre d'analyse consiste à effectuer un étalonnage temporel et à convertir les fichiers FITS en fichiers CSV.

### Github
[https://github.com/YuukiWada/belisama-analysis](https://github.com/YuukiWada/belisama-analysis)

### Plate-forme soutenue
- Mac OS X
- Linux
- (il devrait fonctionner sur les machines Windows dans lesquelles Python est installé).

### Environnement de test
- MacBook Air (Rétine, 13 pouces, 2018)
- macOS Mojave (Version 10.14.4)
- Python 3.7.7
 - astropy 4.0.1.post1
 - matplotlib 3.2.2
 - numpy 1.19.0

## Installation
### Logiciels nécessaires
- Python (la version 3.x est requise)
 - astropy
 - matplotlib
 - numpy


 Les bibliothèques peuvent être installées par les commandes :
 ```
 python -m pip install astropy
 python -m pip install matplotlib
 python -m pip install numpy
 ```

### Cloner les scripts en local
```
git clone https://github.com/YuukiWada/belisama-analysis.git
```

## Utilisation
### Scripts en pipeline
Il existe deux scripts pour les processus de pipeline :
```
pipeline/fits2csv.py
pipeline/fits2csv_batch.py
```

fits2csv.py convertit un fichier FITS en un fichier CSV. Son utilisation est
```
python fits2csv.py <fichier FITS d'entrée> <répertoire de sortie>
```

fits2csv.py interprète le fichier FITS d'entrée, et sauvegarde ses données dans le répertoire de sortie indiqué. Lorsque les commandes
```
python fits2csv.py 20200820_140005.fits.gz ./csv
```
est exécuté,
```
./csv/20200820_140005_ch0.csv.gz
./csv/20200820_140005_ch1.csv.gz
./csv/20200820_140005_ch2.csv.gz
./csv/20200820_140005_ch3.csv.gz
```
sera créé. Comme l'instrument dispose de quatre canaux d'entrée, les données de chaque canal d'entrée sont enregistrées séparément. Si un canal d'entrée n'a pas de données, aucun fichier CSV de ce canal ne sera créé. Par défaut, le fichier CSV de sortie est compressé au format gzip. Utilisez `zless` pour jeter un coup d'oeil aux fichiers compressés.

Le fichier CSV de sortie contient des lignes
```
1511517035.266076,56,0
1511517035.335293,1196,0
1511517035.391294,120,0
1511517035.458569,49,0
...
```
Chaque ligne correspond à un événement photonique détecté par l'instrument. La première colonne contient le temps de détection dans l'unité UNIXTIME. Si les signaux GPS sont correctement reçus par les instruments, la précision du temps est meilleure que 1 us. Si les signaux GPS sont perdus, le script tente de calibrer la synchronisation avec le temps PC de l'instrument. Dans ce cas, la précision de la synchronisation est de +/- 1 seconde lorsque le temps PC est bien ajusté par NTP. Si le temps PC n'est pas bien ajusté et que les signaux GPS sont perdus, la précision du chronométrage n'est pas fiable.

La deuxième colonne contient l'énergie des événements photoniques dans l'unité de canal. Cette valeur varie de 0 à 2048. Un calibrage de l'énergie est nécessaire pour obtenir l'énergie de chaque photon dans l'unité de MeV. La façon la plus courante de calibrer l'énergie est d'utiliser des sources de calibrage : 0,662 MeV de 137Cs. Il est également pratique de détecter la ligne 1,46 MeV de 40K et 2,61 MeV de 208Tl. Le 40K et le 208Tl sont tous deux des isotopes naturels et ces raies peuvent être détectées en tant que fond environnemental naturel. Lorsque la ligne 1,46 MeV est à 140 canaux et la ligne 2,61 MeV à 247, la fonction d'étalonnage
```
Énergie (MeV) = a + b * canal
a=1.46-140.0*b
b=(2.61-1.46)/(247.0-140.0)
```
peuvent être obtenus.

La troisième colonne contient les comptes morts : le nombre de photons qui ont été déclenchés par l'instrument entre le dernier enregistrement de photons (dans la ligne précédente) mais qui n'ont pas été enregistrés en raison d'un dépassement de tampon. En fonctionnement normal, le nombre de photons morts est égal à 0, mais il augmente lorsque le nombre de photons
détecté instantanément et les données sur les photons ne peuvent pas être transportées du FPGA à Raspberry Pi, ou bien Raspberry Pi a beaucoup d'autres processus de fond qui occupent les ressources de l'unité centrale.

Le fichier `fits2csv_batch.py` convertit plusieurs fichiers FITS en fichiers CSV. Son utilisation est
```
python fits2csv_batch.py <répertoire d'entrée> <répertoire de sortie>
```

Lorsque les commandes
```
python fits2csv.py ./fits ./csv
```
est exécuté, le script tente de trouver les fichiers `*.fits` et `*.fits.gz` dans `./fits`, et tous les fichiers FITS du répertoire sont convertis au format CSV. L'autre fonction est la même que celle de `fits2csv.py`.

### Scripts d'analyse
Il y a six scripts à analyser :
```
scripts/spec_fits.py
scripts/spec_gzip.py
scripts/spec_gzip_calibration.py
scripts/lightcurve_fits.py
scripts/lightcurve_gzip.py
scripts/lightcurve_gzip_calibration.py
```

`spec_fits.py` génère un spectre d'énergie dans l'unité de canal. L'utilisation est
```
python spec_fits.py <fichier d'entrée> <canal adc> <binning (option)>
```
Ce script est utile pour examiner rapidement le spectre énergétique d'un fichier FITS avant de le convertir en CSV. Le canal ADC d'entrée doit être spécifié. Lorsque le binnning est indiqué, le spectre d'énergie sera binné.

`spec_gzip.py` génère un spectre d'énergie dans l'unité de canal à partir d'un fichier CSV converti. L'utilisation est
```
python spec_gzip.py <fichier d'entrée> <binning (option)>
```

`spec_gzip_calibration.py` génère un spectre d'énergie dans l'unité MeV à partir d'un fichier CSV converti. L'utilisation est
```
python spec_gzip.py <input file> <p0> <p1> <binning (option)>
```
p0 et p1 sont les paramètres d'une courbe d'étalonnage donnée par
```
Energie (MeV) = p0 + Canal * p1".
```
L'exemple de la courbe d'étalonnage est décrit ci-dessus.

Le fichier `lightcurve_fits.py` génère une courbe de lumière ou un historique du taux de comptage. L'utilisation est
```
python lightcurve_fits.py <input file> <adc channel> <bin width (sec)> <lower threshold> <upper threshold>
```
Ce script est utile pour visualiser rapidement une courbe de lumière d'un fichier FITS avant de le convertir en CSV. Le canal ADC d'entrée doit être spécifié. Les seuils doivent être indiqués dans l'unité du canal.

Le script `lightcurve_gzip.py` génère une courbe de lumière ou un historique des taux de comptage à partir d'un fichier CSV converti. L'utilisation est
```
python lightcurve_gzip.py <fichier d'entrée> <largeur de la cellule (sec)> <seuil inférieur> <seuil supérieur>
```
Les seuils doivent être indiqués dans l'unité de la chaîne.

Le fichier `lightcurve_gzip_calibration.py` génère une courbe de lumière ou un historique des taux de comptage à partir d'un fichier CSV converti. Les seuils d'énergie peuvent être donnés dans l'unité MeV. L'utilisation est
```
python lightcurve_gzip.py <input file> <bin width (sec)> <p0> <p1> <lower threshold (MeV)> <upper threshold (MeV)>
```
p0 et p1 sont les mêmes que `spec_gzip_calibration.py`.

## Données d'échantillon
Un échantillon de fichier FITS et un fichier CSV converti sont stockés dans "samples/".
```
samples/fits/20180312_105530.fits.gz
samples/csv/20180312_105530_ch0.csv.gz
```

