## TODOLIST
Map usb ports
copy master sd card

- synchronizacja czasu na raspberry
- tagi na zawodnikow
- ile chcemy maksymalnie wyslac wiadomosci przez Rocka? Czy zabezpieczenie w postaci wylaczenia wysylki jest wystarczajace?
- co ile chcemy odbierac wiadomosc od Rocka? - 60sek
- ustawic deviceId inne na drugim raspberry/i ttyUSB
- sprawdzic na dwoch urzadzeniach wartosci w plikach konfiguracyjnych, w szczegolnosci antReader.cfg
- ustawic parametry na minimalny/maksymalny interwal wysylki wiadomosci. Zakladamy np. ze nie chcemy wysylac wiadomosci czesciej niz minuta, ale tez nie rzadziej niz co godzina
- regulacja glosnosci w glosniku jesli chcemy z niego skorzystac
- upewnienie sie ze na obydwu maszynach mamy ten sam, najswiezszy kod z git-a
- gdzie jest rock service w git?
- opisanie puszek
- wylaczenie bluetooth/wifi?
- instrukcje obslugi
- 

TESTY:
- ostatecznie dzialanie takie samo na obydwu maszynach (sensory, skrypty ladujace i startujace)
- testy komunikatow z satelity do Raspberry
- przepiecie modemu - czemu nie lapie sygnalu? Czy txFailed traktujemy tak samo jak ROCK Exception? Co wyrzuca po przepieciu? Chyba tylko sygnalu nie lapie?
- test wyslania wiadomosci w regularnym interwale
- test zmiany zawodnika - wszystkie tagi
- test konca plywania - zdarzenie '100'
- test wysylki z gps 0.0/0.0 (zakrycie gps)
- restart Raspberry (wiele razy, w roznych momentach - co z serwisami? Powinny automatycznie wstac. Co z modemem? Czy wysyla, czy w dobrej kolejnosci?)
- przylozenie 100 a potem normalnego
- test czy jesli 2x i wiecekj odbijam rfid to wysle tylko raz
