"""
Sekoitusfunktiot GSR-mallin mukaisesti.

Leikkauspiste on parametrisoitu kolmella jakaumalla:
  - "beta"      : betavariate(2,2) — symmetrinen, keskellä todennäköisempi (oletus)
  - "binomial"  : binomial(n, 0.5) — GSR-mallin teoreettinen jakauma
  - "uniform"   : tasajakauma — naivi verrokki
"""
import random
import numpy as np

LeikkausJakauma = str  # "beta" | "binomial" | "uniform"


def _leikkauskohta(n: int, jakauma: LeikkausJakauma) -> int:
    if jakauma == "beta":
        c = int(random.betavariate(2, 2) * n)
    elif jakauma == "binomial":
        c = int(np.random.binomial(n, 0.5))
    elif jakauma == "uniform":
        c = random.randint(0, n)
    else:
        raise ValueError(f"Tuntematon jakauma: '{jakauma}'. Valitse 'beta', 'binomial' tai 'uniform'.")
    return max(1, min(n - 1, c))


def riffle_shuffle(pakka: list, jakauma: LeikkausJakauma = "beta") -> list:
    """GSR-mallin mukainen riffle-sekoitus."""
    n = len(pakka)
    c = _leikkauskohta(n, jakauma)
    vasen = pakka[:c]
    oikea = pakka[c:]

    tulos = []
    i, j = 0, 0
    while i < len(vasen) or j < len(oikea):
        if i < len(vasen) and (
            j >= len(oikea)
            or random.random() < (len(vasen) - i) / (len(vasen) - i + len(oikea) - j)
        ):
            tulos.append(vasen[i])
            i += 1
        else:
            tulos.append(oikea[j])
            j += 1
    return tulos


def strip_shuffle(pakka: list) -> list:
    """Ottaa 1–5 kortin nippuja pakan päältä ja pinoaa uuteen pakkaan."""
    jaljella = pakka[:]
    niput = []
    while jaljella:
        nipun_koko = min(random.randint(1, 5), len(jaljella))
        niput.append(jaljella[:nipun_koko])
        jaljella = jaljella[nipun_koko:]
    niput.reverse()
    return [k for nippu in niput for k in nippu]


def leikkaa_pakka(pakka: list, jakauma: LeikkausJakauma = "beta") -> list:
    n = len(pakka)
    c = _leikkauskohta(n, jakauma)
    return pakka[c:] + pakka[:c]