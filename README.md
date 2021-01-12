# Watnu?!

## FAQ

### Was für ein Dateiformat ist ".stay" und warum wird nicht JSON oder YAML verwendet?
JSON ist gut geeignet für Maschine-Maschine Kommunikation, aber schlecht geeignet für Menschen.

YAML ist zwar leicht lesbar von Menschen, aber die Spezifikation ist unnötig kompliziert und macht viel zu viel (teilweise mit Sicherheitsproblemen), weswegen strict_yaml entwickelt wurde.

STAY wurde als simple Alternative von mir entwickelt. Es macht sich beim Einlesen der Datei die mächtige Typkonvertierung und -prüfung von pydantic zunutze und kann so auf inline Typisierung und Escaping von Sonderzeichen verzichten, was .stay-Dateien wesentlich übersichtlicher und leichter zu editieren macht.


Quellen:
* https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5395635/
  Identifying the Best Times for Cognitive Functioning Using New Methods: Matching University Times to Undergraduate Chronotypes
