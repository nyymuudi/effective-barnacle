"""
Monte Carlo -simulaattori GSR-sekoituksen tilastolliseen analyysiin.

Sisältää kolme simulaatiotyyppiä:
  1. Perussimulaatio (GSR vs Fisher-Yates)
  2. Jakaumavertailu (beta vs binomial vs uniform leikkauspiste)
  3. Keräysstrategioiden konvergenssivertailu
"""
import random
import numpy as np

from ..shuffle import riffle_shuffle, strip_shuffle, leikkaa_pakka
from ..kerays import KERÄYS_STRATEGIAT


JAKAUMAT = ["beta", "binomial", "uniform"]
MAAt = ["♠", "♡", "♢", "♣"]
ARVOt = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


def fisher_yates(pakka: list) -> list:
    tulos = pakka[:]
    random.shuffle(tulos)
    return tulos


def aja_simulaatio(
    n_kortit: int = 52,
    n_iteraatiot: int = 10_000,
    riffle_toistot: int = 4,
    tee_strip: bool = True,
    jakauma: str = "beta",
) -> np.ndarray:
    """
    Ajaa GSR-sekoituksen n_iteraatiot kertaa.
    Palauttaa (n_kortit, n_kortit) counts-matriisin.
    """
    pakka = list(range(n_kortit))
    counts = np.zeros((n_kortit, n_kortit), dtype=np.int32)

    for _ in range(n_iteraatiot):
        sekoitettu = pakka[:]
        for i in range(riffle_toistot):
            sekoitettu = riffle_shuffle(sekoitettu, jakauma=jakauma)
            if tee_strip and i == 1:
                sekoitettu = strip_shuffle(sekoitettu)
        sekoitettu = leikkaa_pakka(sekoitettu, jakauma=jakauma)
        for paikka, kortti in enumerate(sekoitettu):
            counts[kortti, paikka] += 1

    return counts


def aja_fisher_yates_simulaatio(
    n_kortit: int = 52,
    n_iteraatiot: int = 10_000,
) -> np.ndarray:
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
    jakauma: str = "beta",
) -> dict[int, np.ndarray]:
    """Ajaa simulaation riffle-toistomäärillä 1..max_riffle."""
    return {
        k: aja_simulaatio(n_kortit, n_iteraatiot, riffle_toistot=k,
                          tee_strip=False, jakauma=jakauma)
        for k in range(1, max_riffle + 1)
    }


def aja_jakaumavertailu(
    n_kortit: int = 52,
    n_iteraatiot: int = 10_000,
    riffle_toistot: int = 4,
) -> dict[str, np.ndarray]:
    """
    Laajennus 1: Herkkyysanalyysi leikkauspistejakaumalle.

    Ajaa saman simulaation kolmella jakaumalla (beta, binomial, uniform)
    sekä Fisher-Yates referenssinä.

    Vastaa kysymykseen: onko betavariate(2,2) perusteltua binomiin nähden?
    """
    tulokset = {
        jakauma: aja_simulaatio(
            n_kortit, n_iteraatiot,
            riffle_toistot=riffle_toistot,
            jakauma=jakauma,
        )
        for jakauma in JAKAUMAT
    }
    tulokset["fisher_yates"] = aja_fisher_yates_simulaatio(n_kortit, n_iteraatiot)
    return tulokset


def _kortti_indeksiksi(kortti) -> int:
    return MAAt.index(kortti.maa) * 13 + ARVOt.index(kortti.arvo)


def _indeksi_kortiksi(idx):
    from ..models import Kortti
    return Kortti(MAAt[idx // 13], ARVOt[idx % 13])


def aja_strategiavertailu(
    n_kortit: int = 52,
    n_iteraatiot: int = 10_000,
    max_riffle: int = 10,
    jakauma: str = "beta",
) -> dict[str, dict[int, np.ndarray]]:
    """
    Laajennus 2: Keräysstrategioiden konvergenssivertailu.

    Ajaa konvergenssianalyysin molemmilla keräysstrategioilla käyttäen
    oikeaa EdellinenJako-oliota.

    Vastaa kysymykseen: vaikuttaako keräysjärjestys konvergenssiin?

    Palauttaa:
        {strategia_nimi: {riffle_toistot: counts-matriisi}}
    """
    from ..models import Kortti, Pelaaja, Käsi, EdellinenJako

    def tee_jako():
        """Vakiojako + jäljelle jääneet kortit pohjalle — kaikki 52 mukana."""
        kaikki = [Kortti(m, a) for m in MAAt for a in ARVOt]
        pelaajat = [Pelaaja(f"P{i}", i) for i in range(1, 7)]
        kädet = [Käsi(pelaajat[i], kaikki[i*2:(i+1)*2]) for i in range(6)]
        kädet[0].voittiko = True
        kädet[0].muckasiko = False
        jako = EdellinenJako(
            poltetut=kaikki[12:15],
            yhteiset=kaikki[15:20],
            kädet=kädet,
        )
        # Jäljelle jääneet 32 korttia (ei jaettu) — kerätään pakan pohjalle
        jako._jäljellä = kaikki[20:]
        return jako

    tulokset: dict[str, dict[int, np.ndarray]] = {}

    for strategia_nimi, strategia_fn in KERÄYS_STRATEGIAT.items():
        counts_per_riffle: dict[int, np.ndarray] = {}

        for k in range(1, max_riffle + 1):
            counts = np.zeros((n_kortit, n_kortit), dtype=np.int32)

            for _ in range(n_iteraatiot):
                jako = tee_jako()
                pakka = strategia_fn(jako)
                # Lisätään jakamatta jääneet kortit pakan pohjalle
                pakka = getattr(jako, '_jäljellä', []) + pakka

                # Sekoitus indeksitasolla suorituskyvyn vuoksi
                indeksit = [_kortti_indeksiksi(k) for k in pakka]
                for i in range(k):
                    kortit = [_indeksi_kortiksi(idx) for idx in indeksit]
                    kortit = riffle_shuffle(kortit, jakauma=jakauma)
                    if i == 1:
                        kortit = strip_shuffle(kortit)
                    indeksit = [_kortti_indeksiksi(k) for k in kortit]

                kortit = [_indeksi_kortiksi(idx) for idx in indeksit]
                kortit = leikkaa_pakka(kortit, jakauma=jakauma)
                indeksit = [_kortti_indeksiksi(k) for k in kortit]

                for paikka, kortti_idx in enumerate(indeksit):
                    counts[kortti_idx, paikka] += 1

            counts_per_riffle[k] = counts

        tulokset[strategia_nimi] = counts_per_riffle

    return tulokset