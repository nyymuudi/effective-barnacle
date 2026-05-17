"""
Testit sekoitusfunktioille: riffle_shuffle, strip_shuffle, leikkaa_pakka.

Keskeinen invariantti kaikissa sekoituksissa:
  - Korttien lukumäärä säilyy
  - Korttijoukko (multiset) säilyy — ei katoamisia eikä duplikaatteja
  - Järjestys muuttuu tilastollisesti
"""
import pytest
from collections import Counter
from realistinen_korttisekoitus.shuffle import riffle_shuffle, strip_shuffle, leikkaa_pakka
from realistinen_korttisekoitus.models import Kortti


def kortti_multiset(pakka: list[Kortti]) -> Counter:
    return Counter((k.maa, k.arvo) for k in pakka)


class TestRiffleShuffle:
    def test_säilyttää_kortit(self, täysi_pakka):
        tulos = riffle_shuffle(täysi_pakka)
        assert kortti_multiset(tulos) == kortti_multiset(täysi_pakka)

    def test_säilyttää_lukumäärän(self, täysi_pakka):
        assert len(riffle_shuffle(täysi_pakka)) == 52

    def test_muuttaa_järjestystä(self, täysi_pakka):
        """Tilastollinen testi: 1000 shufflesta vähintään 99% muuttaa järjestystä."""
        muuttui = sum(
            riffle_shuffle(täysi_pakka) != täysi_pakka
            for _ in range(1000)
        )
        assert muuttui >= 990

    def test_pieni_pakka(self):
        """Edge case: 2 kortin pakka."""
        pakka = [Kortti("♠", "A"), Kortti("♡", "K")]
        tulos = riffle_shuffle(pakka)
        assert len(tulos) == 2
        assert kortti_multiset(tulos) == kortti_multiset(pakka)

    def test_ei_muokkaa_alkuperäistä(self, täysi_pakka):
        alkuperäinen = täysi_pakka[:]
        riffle_shuffle(täysi_pakka)
        assert täysi_pakka == alkuperäinen


class TestStripShuffle:
    def test_säilyttää_kortit(self, täysi_pakka):
        tulos = strip_shuffle(täysi_pakka)
        assert kortti_multiset(tulos) == kortti_multiset(täysi_pakka)

    def test_säilyttää_lukumäärän(self, täysi_pakka):
        assert len(strip_shuffle(täysi_pakka)) == 52

    def test_muuttaa_järjestystä(self, täysi_pakka):
        muuttui = sum(
            strip_shuffle(täysi_pakka) != täysi_pakka
            for _ in range(1000)
        )
        assert muuttui >= 900  # strip on deterministisempi kuin riffle

    def test_pieni_pakka(self):
        pakka = [Kortti("♠", "A"), Kortti("♡", "K"), Kortti("♢", "Q")]
        tulos = strip_shuffle(pakka)
        assert kortti_multiset(tulos) == kortti_multiset(pakka)


class TestLeikkaaPakka:
    def test_säilyttää_kortit(self, täysi_pakka):
        tulos = leikkaa_pakka(täysi_pakka)
        assert kortti_multiset(tulos) == kortti_multiset(täysi_pakka)

    def test_säilyttää_lukumäärän(self, täysi_pakka):
        assert len(leikkaa_pakka(täysi_pakka)) == 52

    def test_leikkaus_on_rotaatio(self, täysi_pakka):
        """Leikkaus on aina rotaatio — alkuperäiset kortit löytyvät yhtenäisenä jonona."""
        tulos = leikkaa_pakka(täysi_pakka)
        kaksinkertainen = täysi_pakka + täysi_pakka
        # Etsi tulos kaksinkertaisesta listasta
        n = len(tulos)
        löytyi = any(
            kaksinkertainen[i:i+n] == tulos
            for i in range(n)
        )
        assert löytyi