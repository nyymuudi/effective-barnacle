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


KERÄYS_STRATEGIAT: dict[str, KeräysStrategia] = {
    "perus": _perus_keräys,
    "voittaja_päälle": _voittaja_päälle,
}