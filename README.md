# Watnu?!

## FAQ
### Was ist das für eine Schriftart?
https://sansforgetica.rmit/
Sans Forgetica is designed for non-commercial use only. It is bound by a creative commons, non-commercial, attributed (CCBYNC) license.
https://www.1001fonts.com/exo-2-0-font.html#more


### Was ist das für ein Farbschema?
https://en.wikipedia.org/wiki/Solarized_(color_scheme)
### Was für ein Dateiformat ist ".stay" und warum wird nicht JSON oder YAML verwendet?
JSON ist gut geeignet für Maschine-Maschine Kommunikation, aber schlecht geeignet für Menschen.

YAML ist zwar leicht lesbar von Menschen, aber die Spezifikation ist unnötig kompliziert und macht viel zu viel (teilweise mit Sicherheitsproblemen), weswegen strict_yaml entwickelt wurde.

STAY wurde als simple Alternative von mir entwickelt. Es macht sich beim Einlesen der Datei die mächtige Typkonvertierung und -prüfung von pydantic zunutze und kann so auf inline Typisierung und Escaping von Sonderzeichen verzichten, was .stay-Dateien wesentlich übersichtlicher und leichter zu editieren macht.