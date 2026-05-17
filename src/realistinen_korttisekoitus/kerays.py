import random
from typing import Callable
from .models import EdellinenJako, Kortti

KeräysStrategia = Callable[[EdellinenJako], list[Kortti]]


def _perus_keräys(jako: EdellinenJako) -> list[Kortti]:
    """
    Oletusstrategia.
    Järjestys: poltetut (pohja) → ei-voittajat → voittajat → yhteiset (päällimmäisenä).
    """
    pakka: list[Kortti] = []

    pakka.extend(jako.poltetut)

    ei_voittajat = sorted(
        (k for k in jako.kädet if not k.voittiko),
        key=lambda k: k.pelaaja.paikka,
    )
    for kasi in ei_voittajat:
        pakka.extend(kasi.kortit)

    for kasi in jako.kädet:
        if kasi.voittiko:
            pakka.extend(kasi.kortit)

    pakka.extend(jako.yhteiset)
    return pakka


def _voittaja_päälle(jako: EdellinenJako) -> list[Kortti]:
    """
    Voittajan käsi kerätään viimeisenä pakan päälle.
    Järjestys: poltetut (pohja) → ei-voittajat → yhteiset → voittajat (päällimmäisenä).
    """
    pakka: list[Kortti] = []

    pakka.extend(jako.poltetut)

    ei_voittajat = sorted(
        (k for k in jako.kädet if not k.voittiko),
        key=lambda k: k.pelaaja.paikka,
    )
    for kasi in ei_voittajat:
        pakka.extend(kasi.kortit)

    pakka.extend(jako.yhteiset)

    for kasi in jako.kädet:
        if kasi.voittiko:
            pakka.extend(kasi.kortit)

    return pakka


def _wash_keräys(jako: EdellinenJako) -> list[Kortti]:
    """
    Wash/Scramble-strategia: kortit levitetään pöydälle ja sekoitetaan
    käsin ennen keräämistä — kasinoissa käytetty käytäntö erityisesti
    uuden pakan käyttöönoton yhteydessä.

    Fyysinen vastine: dealer liu'uttaa kortteja satunnaisesti pöydällä
    ennen kuin kerää ne pakaksi. Tämä rikkoo collection-order-rakenteen
    tehokkaammin kuin riffle-sekoitus pienellä toistomäärällä.

    Mallinnus: kortit kerätään perus-järjestyksessä, jonka jälkeen
    pakka jaetaan satunnaisiin ryhmiin ja ryhmät sekoitetaan keskenään
    simuloiden pöytälevitystä. Lopputulos on lähempänä uniformia jakaumaa
    kuin mikään keräysstrategia yksinään — mutta ei täysin satunnainen.
    """
    # Kerätään ensin perusjärjestyksessä
    pakka = _perus_keräys(jako)
    n = len(pakka)

    # Jaetaan satunnaisiin ryhmiin (3-7 korttia) ja sekoitetaan ryhmät
    ryhmät: list[list[Kortti]] = []
    i = 0
    while i < n:
        koko = random.randint(3, 7)
        ryhmät.append(pakka[i:i+koko])
        i += koko

    random.shuffle(ryhmät)

    # Jokaisen ryhmän sisällä kortit sekoitetaan myös
    tulos: list[Kortti] = []
    for ryhmä in ryhmät:
        random.shuffle(ryhmä)
        tulos.extend(ryhmä)

    return tulos


KERÄYS_STRATEGIAT: dict[str, KeräysStrategia] = {
    "perus": _perus_keräys,
    "voittaja_päälle": _voittaja_päälle,
    "wash": _wash_keräys,
}