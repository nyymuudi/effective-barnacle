"""
Monte Carlo -simulaattori GSR-sekoituksen tilastolliseen analyysiin.

Tuottaa raakadatan metrics.py:lle ja visualize.py:lle:
  - Korttipaikkajakauma eri riffle-toistomäärillä
  - GSR vs Fisher-Yates vertailudata
"""
import random
import numpy as np
from typing import Callable

from ..shuffle import riffle_shuffle, strip_shuffle, leikkaa_pakka


def fisher_yates(pakka: list) -> list:
    """Standardi Fisher-Yates in-place, palautetaan uutena listana vertailua varten."""
    tulos = pakka[:]
    random.shuffle(tulos)
    return tulos


def aja_simulaatio(
    n_kortit: int = 52,
    n_iteraatiot: int = 10_000,
    riffle_toistot: int = 4,
    tee_strip: bool = True,
) -> np.ndarray:
    """
    Ajaa GSR-sekoituksen n_iteraatiot kertaa ja tallentaa jokaisen kortin
    loppupaikan.

    Palauttaa:
        position_counts: (n_kortit, n_kortit) matriisi, jossa
                         position_counts[i, j] = kuinka monta kertaa
                         kortti i päätyi paikkaan j.
    """
    pakka = list(range(n_kortit))
    counts = np.zeros((n_kortit, n_kortit), dtype=np.int32)

    for _ in range(n_iteraatiot):
        sekoitettu = pakka[:]
        for i in range(riffle_toistot):
            sekoitettu = riffle_shuffle(sekoitettu)
            if tee_strip and i == 1:
                sekoitettu = strip_shuffle(sekoitettu)
        sekoitettu = leikkaa_pakka(sekoitettu)

        for paikka, kortti in enumerate(sekoitettu):
            counts[kortti, paikka] += 1

    return counts


def aja_fisher_yates_simulaatio(
    n_kortit: int = 52,
    n_iteraatiot: int = 10_000,
) -> np.ndarray:
    """
    Sama simulaatio Fisher-Yatesilla vertailupohjaksi.
    """
    pakka = list(range(n_kortit))
    counts = np.zeros((n_kortit, n_kortit), dtype=np.int32)

    for _ in range(n_iteraatiot):
        sekoitettu = fisher_yates(pakka)
        for paikka, kortti in enumerate(sekoitettu):
            counts[kortti, paikka] += 1

    return counts


def aja_konvergenssianalyysi(
    n_kortit: int = 52,
    n_iteraatiot: int = 10_000,
    max_riffle: int = 10,
) -> dict[int, np.ndarray]:
    """
    Ajaa simulaation riffle-toistomäärillä 1..max_riffle.
    Palauttaa sanakirjan {riffle_toistot: counts-matriisi}.
    Käytetään konvergenssikäyrän piirtämiseen.
    """
    return {
        k: aja_simulaatio(n_kortit, n_iteraatiot, riffle_toistot=k, tee_strip=False)
        for k in range(1, max_riffle + 1)
    }