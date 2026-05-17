"""
Tilastolliset mittarit sekoituksen laadun arviointiin.

Mittarit:
  - Shannon-entropia korttipaikkajakaumalle
  - Permutation bias (chi-squared -testi uniformia jakaumaa vastaan)
  - Total variation distance uniformista jakaumasta
"""
import numpy as np
from scipy.stats import chisquare


def laske_entropia(counts: np.ndarray) -> np.ndarray:
    """
    Laskee Shannon-entropian jokaiselle kortille sen paikkajakauman perusteella.

    Maksimientropia log2(n) ≈ 5.70 bittiä (n=52) vastaa täydellistä uniformia jakaumaa.

    Args:
        counts: (n, n) matriisi jossa counts[i, j] = kortti i paikan j frekv.

    Palauttaa:
        entropiat: (n,) vektori, yksi entropiarvo per kortti.
    """
    frekvenssit = counts / counts.sum(axis=1, keepdims=True)
    # Vältetään log(0): nollataan nolla-arvot
    frekvenssit = np.where(frekvenssit > 0, frekvenssit, 1e-10)
    return -np.sum(frekvenssit * np.log2(frekvenssit), axis=1)


def laske_permutation_bias(counts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Chi-squared -testi jokaiselle kortille: onko paikkajakauma uniformi?

    H0: kortti i jakaantuu tasaisesti kaikkiin paikkoihin.
    Pieni p-arvo → merkittävä bias.

    Palauttaa:
        chi2_stats: (n,) chi-squared -statistiikka per kortti
        p_arvot:    (n,) p-arvo per kortti
    """
    n = counts.shape[0]
    odotettu = counts.sum(axis=1, keepdims=True) / n  # uniform odotusarvo

    chi2_stats = np.zeros(n)
    p_arvot = np.zeros(n)

    for i in range(n):
        chi2_stats[i], p_arvot[i] = chisquare(counts[i], f_exp=np.full(n, odotettu[i]))

    return chi2_stats, p_arvot


def laske_total_variation_distance(counts: np.ndarray) -> np.ndarray:
    """
    Total variation distance (TVD) uniformista jakaumasta per kortti.

    TVD = 0.5 * Σ |p_i - 1/n|
    TVD = 0 tarkoittaa täydellistä uniformia jakaumaa.
    TVD = 1 tarkoittaa täydellistä deterministisyyttä.

    Palauttaa:
        tvd: (n,) vektori
    """
    n = counts.shape[1]
    frekvenssit = counts / counts.sum(axis=1, keepdims=True)
    return 0.5 * np.sum(np.abs(frekvenssit - 1 / n), axis=1)


def yhteenveto(counts: np.ndarray) -> dict:
    """
    Laskee kaikki mittarit yhdellä kutsulla ja palauttaa yhteenvetosanakirjan.
    """
    entropiat = laske_entropia(counts)
    _, p_arvot = laske_permutation_bias(counts)
    tvd = laske_total_variation_distance(counts)
    max_entropia = np.log2(counts.shape[0])

    return {
        "entropia_keskiarvo": entropiat.mean(),
        "entropia_max": max_entropia,
        "entropia_suhde": entropiat.mean() / max_entropia,  # 1.0 = täydellinen
        "bias_p_mediaani": np.median(p_arvot),
        "bias_merkittavia": int((p_arvot < 0.05).sum()),  # montako korttia biased
        "tvd_keskiarvo": tvd.mean(),
    }