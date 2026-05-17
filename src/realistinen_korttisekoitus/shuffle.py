"""
Sekoitusfunktiot GSR-mallin mukaisesti.

Leikkauspiste on parametrisoitu kolmella jakaumalla:
  - "beta"      : betavariate(2,2) — symmetrinen, keskellä todennäköisempi (oletus)
  - "binomial"  : binomial(n, 0.5) — GSR-mallin teoreettinen jakauma
  - "uniform"   : tasajakauma — naivi verrokki

Imperfect-variantit mallintavat inhimillistä epätarkkuutta DealerProfiili-parametrien avulla.
"""
import math
import random
import numpy as np

LeikkausJakauma = str  # "beta" | "binomial" | "uniform"


def _leikkauskohta(n: int, jakauma: LeikkausJakauma, bias: float = 0.5) -> int:
    """Laskee leikkauskohdan valitulla jakaumalla ja mahdollisella biaksella."""
    if jakauma == "beta":
        # Siirretään betajakauman keskipiste biaksen mukaan
        alpha = 2 + (bias - 0.5) * 8
        beta_ = 2 - (bias - 0.5) * 8
        alpha = max(0.5, alpha)
        beta_ = max(0.5, beta_)
        c = int(random.betavariate(alpha, beta_) * n)
    elif jakauma == "binomial":
        c = int(np.random.binomial(n, bias))
    elif jakauma == "uniform":
        c = random.randint(0, n)
    else:
        raise ValueError(f"Tuntematon jakauma: '{jakauma}'. Valitse 'beta', 'binomial' tai 'uniform'.")
    return max(1, min(n - 1, c))


def riffle_shuffle(pakka: list, jakauma: LeikkausJakauma = "beta") -> list:
    """GSR-mallin mukainen ideaali riffle-sekoitus."""
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


def imperfect_riffle_shuffle(pakka: list, profiili) -> list:
    """
    Inhimillinen riffle-sekoitus DealerProfiili-parametrien mukaan.

    Eroaa ideaalista kolmella tavalla:
      1. Leikkauspiste vinoutuu dominant_hand_bias-parametrin mukaan
      2. pressure_variance lisää satunnaisuutta pudotustodennäköisyyteen
         — korkea arvo tuottaa pitkiä juoksuja samalta puolelta
      3. clump_probability aiheuttaa pareittaisia pudotuksia
         — kortit "tarttuvat" toisiinsa sormien alla
    """
    n = len(pakka)
    c = _leikkauskohta(n, "beta", bias=profiili.dominant_hand_bias)
    vasen = pakka[:c]
    oikea = pakka[c:]

    tulos = []
    i, j = 0, 0

    while i < len(vasen) or j < len(oikea):
        vasen_jaljella = len(vasen) - i
        oikea_jaljella = len(oikea) - j

        if vasen_jaljella == 0:
            tulos.append(oikea[j]); j += 1; continue
        if oikea_jaljella == 0:
            tulos.append(vasen[i]); i += 1; continue

        # Perustodennäköisyys GSR-mallin mukaan
        p_vasen = vasen_jaljella / (vasen_jaljella + oikea_jaljella)

        # pressure_variance lisää kohinaa todennäköisyyteen.
        # Logistinen transformaatio pitää arvon aina (0, 1) välillä
        # ilman keinotekoista klippausta — fysikaalisesti perustellumpi.
        if profiili.pressure_variance > 0:
            noise = random.gauss(0, profiili.pressure_variance)
            logit = math.log(p_vasen / (1 - p_vasen)) + noise
            p_vasen = 1 / (1 + math.exp(-logit))

        # Valitaan puoli
        ota_vasemmalta = random.random() < p_vasen

        # clump_probability: pudotetaan mahdollisesti 2 korttia kerralla
        if random.random() < profiili.clump_probability:
            maara = 2
        else:
            maara = 1

        if ota_vasemmalta:
            for _ in range(min(maara, len(vasen) - i)):
                tulos.append(vasen[i]); i += 1
        else:
            for _ in range(min(maara, len(oikea) - j)):
                tulos.append(oikea[j]); j += 1

    return tulos


def strip_shuffle(pakka: list, strip_irregularity: float = 0.5) -> list:
    """
    Strip shuffle nipun kokovariansilla.

    strip_irregularity = 0   → vakio 3 kortin niput
    strip_irregularity = 1.0 → hyvin epätasaiset niput (1–8 korttia)
    """
    jaljella = pakka[:]
    niput = []
    while jaljella:
        if strip_irregularity > 0:
            koko = max(1, int(random.gauss(3, strip_irregularity * 2)))
        else:
            koko = 3
        nipun_koko = min(koko, len(jaljella))
        niput.append(jaljella[:nipun_koko])
        jaljella = jaljella[nipun_koko:]
    niput.reverse()
    return [k for nippu in niput for k in nippu]


def leikkaa_pakka(pakka: list, jakauma: LeikkausJakauma = "beta", bias: float = 0.5) -> list:
    n = len(pakka)
    c = _leikkauskohta(n, jakauma, bias=bias)
    return pakka[c:] + pakka[:c]