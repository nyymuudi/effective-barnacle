"""
Testit keräyslogiikalle (kerays.py) ja pääputkelle (engine.py).
"""
import pytest
from collections import Counter
from realistinen_korttisekoitus.kerays import KERÄYS_STRATEGIAT

kerää_kortit = KERÄYS_STRATEGIAT["perus"]
from realistinen_korttisekoitus.engine import valmistele_pakka_seuraavaa_jakoa_varten
from realistinen_korttisekoitus.models import Kortti, Pelaaja, Käsi, EdellinenJako


def kortti_multiset(pakka: list[Kortti]) -> Counter:
    return Counter((k.maa, k.arvo) for k in pakka)


def kaikki_kortit_jaossa(jako: EdellinenJako) -> list[Kortti]:
    """Palauttaa kaikki kortit jaosta riippumatta niiden tilasta."""
    kortit = []
    kortit.extend(jako.poltetut)
    kortit.extend(jako.yhteiset)
    for käsi in jako.kädet:
        kortit.extend(käsi.kortit)
    return kortit


class TestKeräysFunktiolla:
    def test_kaikki_kortit_kerätään(self, perus_jako):
        """Yksikään kortti ei katoa keräysvaiheessa."""
        kerätty = kerää_kortit(perus_jako)
        assert kortti_multiset(kerätty) == kortti_multiset(kaikki_kortit_jaossa(perus_jako))

    def test_ei_duplikaatteja(self, perus_jako):
        kerätty = kerää_kortit(perus_jako)
        assert len(kerätty) == len(set((k.maa, k.arvo) for k in kerätty))

    def test_showdown_kortit_kerätään(self, perus_jako):
        """Häviäjän näyttämät kortit (muckasiko=False) eivät katoa."""
        kerätty = kerää_kortit(perus_jako)
        # p2 näytti kätensä: ♣7 ja ♢8
        näytetyt = [Kortti("♣", "7"), Kortti("♢", "8")]
        for kortti in näytetyt:
            assert kortti in kerätty

    def test_split_pot_molemmat_voittajat_kerätään(self, split_pot_jako):
        """Split potissa molempien voittajien kortit kerätään."""
        kerätty = kerää_kortit(split_pot_jako)
        assert kortti_multiset(kerätty) == kortti_multiset(kaikki_kortit_jaossa(split_pot_jako))

    def test_voittaja_joka_muckasi(self, voittaja_muckasi_jako):
        """Voittaja joka muckasi — kortit silti kerätään."""
        kerätty = kerää_kortit(voittaja_muckasi_jako)
        assert kortti_multiset(kerätty) == kortti_multiset(kaikki_kortit_jaossa(voittaja_muckasi_jako))

    def test_keräysjärjestys_paikan_mukaan(self):
        """Ei-voittajat kerätään pöytäpaikan mukaisessa järjestyksessä."""
        p1 = Pelaaja("A", 3)  # myöhäinen paikka
        p2 = Pelaaja("B", 1)  # varhainen paikka
        p3 = Pelaaja("C", 2)
        jako = EdellinenJako(
            poltetut=[],
            yhteiset=[],
            kädet=[
                Käsi(p1, [Kortti("♠", "2")], voittiko=True),
                Käsi(p2, [Kortti("♡", "3")]),  # paikka 1 → ensin
                Käsi(p3, [Kortti("♢", "4")]),  # paikka 2 → toiseksi
            ],
        )
        kerätty = kerää_kortit(jako)
        # p2 (paikka 1) ennen p3:ta (paikka 2)
        idx_p2 = next(i for i, k in enumerate(kerätty) if k == Kortti("♡", "3"))
        idx_p3 = next(i for i, k in enumerate(kerätty) if k == Kortti("♢", "4"))
        assert idx_p2 < idx_p3


class TestEngine:
    def test_palauttaa_kaikki_kortit(self, perus_jako):
        """Koko putki säilyttää kortit."""
        tulos = valmistele_pakka_seuraavaa_jakoa_varten(perus_jako)
        alkuperäiset = kaikki_kortit_jaossa(perus_jako)
        assert kortti_multiset(tulos) == kortti_multiset(alkuperäiset)

    def test_palauttaa_listan(self, perus_jako):
        tulos = valmistele_pakka_seuraavaa_jakoa_varten(perus_jako)
        assert isinstance(tulos, list)
        assert all(isinstance(k, Kortti) for k in tulos)

    def test_eri_riffle_toistot(self, perus_jako):
        for toistot in [1, 4, 7]:
            tulos = valmistele_pakka_seuraavaa_jakoa_varten(perus_jako, riffle_toistot=toistot)
            assert len(tulos) == len(kaikki_kortit_jaossa(perus_jako))

    def test_ilman_strip(self, perus_jako):
        tulos = valmistele_pakka_seuraavaa_jakoa_varten(perus_jako, tee_strip=False)
        assert kortti_multiset(tulos) == kortti_multiset(kaikki_kortit_jaossa(perus_jako))

    def test_deterministisyys_seedillä(self, perus_jako):
        """Sama seed → sama tulos (toistettavuus)."""
        import random
        random.seed(42)
        tulos1 = valmistele_pakka_seuraavaa_jakoa_varten(perus_jako)
        random.seed(42)
        tulos2 = valmistele_pakka_seuraavaa_jakoa_varten(perus_jako)
        assert tulos1 == tulos2


class TestVoittajaPäälleStrategia:
    """Testit voittaja_päälle-keräysstrategialle."""

    def setup_method(self):
        self.kerää = KERÄYS_STRATEGIAT["voittaja_päälle"]

    def test_kaikki_kortit_kerätään(self, perus_jako):
        kerätty = self.kerää(perus_jako)
        assert kortti_multiset(kerätty) == kortti_multiset(kaikki_kortit_jaossa(perus_jako))

    def test_ei_duplikaatteja(self, perus_jako):
        kerätty = self.kerää(perus_jako)
        assert len(kerätty) == len(set((k.maa, k.arvo) for k in kerätty))

    def test_voittajan_kortit_päällimmäisenä(self, perus_jako):
        """Voittajan kortit ovat listan lopussa (päällimmäisenä pakassa)."""
        kerätty = self.kerää(perus_jako)
        voittajan_kortit = [k.kortit for k in perus_jako.kädet if k.voittiko][0]
        assert kerätty[-len(voittajan_kortit):] == voittajan_kortit

    def test_yhteiset_ennen_voittajaa(self, perus_jako):
        """Yhteiset kortit kerätään ennen voittajan käsiä."""
        kerätty = self.kerää(perus_jako)
        voittajan_kortit = [k.kortit for k in perus_jako.kädet if k.voittiko][0]
        idx_voittaja = kerätty.index(voittajan_kortit[0])
        for yhteinen in perus_jako.yhteiset:
            assert kerätty.index(yhteinen) < idx_voittaja

    def test_split_pot(self, split_pot_jako):
        kerätty = self.kerää(split_pot_jako)
        assert kortti_multiset(kerätty) == kortti_multiset(kaikki_kortit_jaossa(split_pot_jako))

    def test_engine_strategialla(self, perus_jako):
        """Engine hyväksyy voittaja_päälle-strategian."""
        tulos = valmistele_pakka_seuraavaa_jakoa_varten(
            perus_jako, keräys_strategia="voittaja_päälle"
        )
        assert kortti_multiset(tulos) == kortti_multiset(kaikki_kortit_jaossa(perus_jako))

    def test_tuntematon_strategia_nostaa_virheen(self, perus_jako):
        with pytest.raises(ValueError, match="Tuntematon"):
            valmistele_pakka_seuraavaa_jakoa_varten(
                perus_jako, keräys_strategia="ei_ole_olemassa"
            )