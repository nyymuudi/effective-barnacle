from .kerays import KERÄYS_STRATEGIAT
from .shuffle import riffle_shuffle, strip_shuffle, leikkaa_pakka
from .models import EdellinenJako, Kortti


def valmistele_pakka_seuraavaa_jakoa_varten(
    edellinen: EdellinenJako,
    riffle_toistot: int = 4,
    tee_strip: bool = True,
    keräys_strategia: str = "perus",
) -> list[Kortti]:
    """
    Pääputki: kerää kortit valitulla strategialla, sekoita ja leikkaa.

    Args:
        edellinen:         Edellisen jaon tiedot.
        riffle_toistot:    Riffle-sekoitusten määrä (suositus: 4–7).
        tee_strip:         Suoritetaanko strip-sekoitus riffle-sarjan välissä.
        keräys_strategia:  Yksi arvoista 'perus', 'voittaja_päälle', 'poltetut_erikseen'.
    """
    if keräys_strategia not in KERÄYS_STRATEGIAT:
        raise ValueError(
            f"Tuntematon keräysstrategia: '{keräys_strategia}'. "
            f"Validi strategia on yksi seuraavista: {list(KERÄYS_STRATEGIAT)}"
        )

    kerää = KERÄYS_STRATEGIAT[keräys_strategia]
    pakka = kerää(edellinen)

    for i in range(riffle_toistot):
        pakka = riffle_shuffle(pakka)
        if tee_strip and i == 1:
            pakka = strip_shuffle(pakka)

    pakka = leikkaa_pakka(pakka)
    return pakka