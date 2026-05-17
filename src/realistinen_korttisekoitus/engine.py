import random
from .kerays import KERÄYS_STRATEGIAT
from .shuffle import riffle_shuffle, imperfect_riffle_shuffle, strip_shuffle, leikkaa_pakka
from .models import EdellinenJako, Kortti, DealerProfiili, DEALER_PROFIILIT


def valmistele_pakka_seuraavaa_jakoa_varten(
    edellinen: EdellinenJako,
    riffle_toistot: int = 4,
    tee_strip: bool = True,
    keräys_strategia: str = "perus",
    seed: int | None = None,
    dealer_profiili: str | DealerProfiili | None = None,
) -> list[Kortti]:
    """
    Pääputki: kerää kortit valitulla strategialla, sekoita ja leikkaa.

    Args:
        edellinen:         Edellisen jaon tiedot.
        riffle_toistot:    Riffle-sekoitusten määrä (suositus: 4–7).
        tee_strip:         Suoritetaanko strip-sekoitus riffle-sarjan välissä.
        keräys_strategia:  Yksi arvoista 'perus', 'voittaja_päälle'.
        seed:              Satunnaislukusiemen toistettavuutta varten.
        dealer_profiili:   DealerProfiili-olio tai nimi ('ideaali', 'kokenut', 'aloittelija').
                           None = ideaali GSR-malli ilman inhimillistä epätarkkuutta.
    """
    if keräys_strategia not in KERÄYS_STRATEGIAT:
        raise ValueError(
            f"Tuntematon keräysstrategia: '{keräys_strategia}'. "
            f"Validi strategia on yksi seuraavista: {list(KERÄYS_STRATEGIAT)}"
        )

    if seed is not None:
        random.seed(seed)

    # Ratkaistaan profiili
    profiili: DealerProfiili | None = None
    if isinstance(dealer_profiili, str):
        if dealer_profiili not in DEALER_PROFIILIT:
            raise ValueError(
                f"Tuntematon profiili: '{dealer_profiili}'. "
                f"Validi profiili on yksi seuraavista: {list(DEALER_PROFIILIT)}"
            )
        profiili = DEALER_PROFIILIT[dealer_profiili]
    elif isinstance(dealer_profiili, DealerProfiili):
        profiili = dealer_profiili

    kerää = KERÄYS_STRATEGIAT[keräys_strategia]
    pakka = kerää(edellinen)

    for i in range(riffle_toistot):
        if profiili is not None:
            pakka = imperfect_riffle_shuffle(pakka, profiili)
        else:
            pakka = riffle_shuffle(pakka)

        if tee_strip and i == 1:
            irregularity = profiili.strip_irregularity if profiili else 0.5
            pakka = strip_shuffle(pakka, strip_irregularity=irregularity)

    pakka = leikkaa_pakka(pakka)
    return pakka