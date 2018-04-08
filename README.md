# Pràctica 1 Tipologia de dades: Web Scraping

Aquesta pràctica s’emmarca dintre del marc dels estudis de Ciència de Dades de la UOC (Universitat Oberta de Catalunya).

##  Descripció

En aquesta pràctica es tracta d’obtenir les dades d’un lloc web i guardar-les en un fitxer CSV.

La meva pràctica consta d’una aplicació que obté les dades dels tirotejos massius que s’han produït als USA des del 2013. Per obtenir les dades he usat el llenguatge Python i les dades provenen de la web [Gun violence archive](http://www.gunviolencearchive.org/reports/mass-shooting).

## Membres de l’equip

Jo sóc l’únic membre de l’equip: Ramon Maria Gallart Escolà

## Estructura del projecte

El projecte consta de 5 directoris on s’organitza la informació, un fitxer de llicència (`LICENSE`)  i aquest `README`.

### doc

En aquest directori hi ha l’enunciat de la pràctica i les meves respostes.

### logs

L’script que obté les dades dels tirotejos escriu un log rotatiu. Aquest log s’emmagatzema en aquest directori.

### out

En aquest directori es guarda la sortida de l’script (el fitxer CSV). També conté un fitxer de sortida de mostra (`20180407_output-2018.csv`).

### src

En aquest directori hi ha les fonts de l’script.

- **src/incident.py**: defineix una classe Incident amb els atributs necessaris.
- **src/license.py**: la llicència escollida per aquesta pràctica és GNU GPL v3. Aquesta llicència demana que en el cas que l’aplicació sigui de línia de comandes hi hagi dues opcions `-c` i `-w` que expliquin les condicions i les garanties que ofereix l’aplicació. Aquest mòdul de Python realitza aquesta tasca.
- **src/logger.py**: genera un logger mínimamanet configurable.
- **src/shootings.py**: script principal. És l’encarregat d’obtenir les dades i emmagatzemar-les en el fitxer CSV de sortida.

### tools

Conté un fitxer (`requirements.txt`) amb les dependències necessàries per executar l’aplicació.

## Requeriments

Aquest script s’ha desenvolupat i provat usant Python 3.6.3, per tant és recomanable emprar aquesta mateixa versió del llenguatge.

Les instruccions donades en aquest `README` estan fetes tenint en compte que l’usuari final utilitza alguna variant de \*NIX (per exemple macOS, Linux, Unix, etc.). L’script s’ha desenvolupat en un Mac i s’ha provat en Mac i Ubuntu.

## Instal·lació

El primer que hem de fer és baixar el repositori del projecte:

	$ git clone https://github.com/easydevmixin/shootings_crawler.git

En la meva opinió i experiència, la millor manera d’executar una aplicació amb Python és mitjançant l’ús d’entorns virtuals. Per poder crear un entorn virtual necessitem [`virtualenv i pip`](http://www.easydevmixin.com/2015/06/07/virtualenv-and-pip/).

Un cop tenim `pip i virtualenv` i el nostre entorn virtual activat podem instal·lar les dependències amb el fitxer [`requirements.txt`](http://www.easydevmixin.com/2015/06/19/creating-a-requirements-file/).

	$ cd shootings_crawler
	$ pip install -r tools/requirements.txt

## Funcionament

Amb l’entorn virtual activat i les dependències instal·lades és el moment de fer funcionar l’scraper.

	$ cd shootings_crawler/src
	$ python shootings.py --help
	usage: shootings.py [-h] [-c] [-D] [-o OUTPUT] [-t TBR] [-T TRIES] [-w]
	                    [-y YEAR]

	optional arguments:
	  -h, --help            show this help message and exit
	  -c, --conditions      Check out the conditions summary.
	  -D, --debug           Sets logger to log debug events.
	  -o OUTPUT, --output OUTPUT
	                        Output filename (default is output.csv).
	  -t TBR, --tbr TBR     Time elapsed between requests in seconds (default 10).
	  -T TRIES, --tries TRIES
	                        Number of times trying to fetch the page (default 3).
	  -w, --warranty        Check out the warranty summary.
	  -y YEAR, --year YEAR  Year of the shootings. Must be on or over 2013.

Amb `--help` podem veure quines són les opcions que tenim disponibles a l’hora de fer córrer l’script.

- **`-h`**: mostra el missatge d’ajuda
- **`-c`**: mostra les condicions sota les quals s’executa el programa (requerit per GNU GPL v3).
- **`-D`**: mode depuració. Deixarà en el registre de sortida tots els missatges de depuració.
- **`-o`**: permet definir el nom del fitxer de sortida. Per defecte és `output.csv`.
- **`-t`**: temps que ha de passar entre peticions. Per defecte és 10 segons. Així si una pàgina té 25 registres de tirotejos amb 25 enllaços diferents, l’script trigarà una mitja de 250 segons en obtenir totes les dades.
- **`-T`**: nombre d’intents abans de donar la pàgina per perduda.
- **`-w`**: mostra la garantia sota la qual s’executa el programa (requerit per GNU GPL v3).
- **`-y`**: any sobre el que es volen obtenir les dades dels tirotejos massius. Ha de ser un any igual o superior a 2013.

Per exemple, si volem executar l’script de forma que volem obtenir les dades dels tirotejos massius ocorreguts l’any 2017, en mode debug i que només hi hagi 3 segons entre peticions, la comanda és la següent:

	$ python shootings.py -y 2017 -D -t 3

## Notes sobre la implementació

S’ha intentat usar el mòdul de Python `urllib.robotparser` per poder parsejar el fitxer `robots.txt` localitzat a [http://www.gunviolencearchive.org/robots.txt](http://www.gunviolencearchive.org/robots.txt) però no ha estat possible, ja que o bé la classe `RobotFileParser` té un error (improbable però no impossible) o bé el fitxer no està ben construït.

	In [1]: from urllib.robotparser import RobotFileParser
	In [2]: r = RobotFileParser()
	In [3]: r.set_url('http://www.gunviolencearchive.org/robots.txt')
	In [4]: r.read()
	In [5]: r.entries
	Out[5]: []

En tot cas l’script no navega per pàgines que estiguin no permeses i el valor de 10 segons per defecte entre peticions està extret directament d’aquest fitxer.

## TBD

Millores a implementar en un futur sense cap ordre específic:

- Afegir la possibilitat que es puguin extreure les dades de més d’un any en la mateixa comanda (per exemple passant una llista d’anys). Actualment es podria aconseguir fent màgia amb la línia de comandaments, però seria molt més útil si es pogués fer amb una opció de l’script.
- Donar l’opció d’exportar les dades en diferents formats, no només en CSV (JSON, YAML, text pla, HTML, etc.)
- Crear una màquina virtual amb Vagrant o Docker de forma que l’usuari final no hagi d’instal·lar res, si no que ja ho tingui tot preparat per executar.

## Recursos

1. Lawson, Richard. *Web Scraping with Python*. 1st ed. Packt Publishing, 2015.
2. Mitchell, Ryan. *Web Scraping with Python, 2nd Edition*. 2nd ed. O’Reilly Media, Inc., 2018.
