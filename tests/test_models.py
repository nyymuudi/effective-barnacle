"""
Testit tietomalleille: Kortti, Pelaaja, Käsi, EdellinenJako.
"""
import pytest
from realistinen_korttisekoitus.models import Kortti, Pelaaja, Käsi, EdellinenJako


class TestKortti:
    def test_repr(self):
        assert repr(Kortti("♠", "A")) == "A♠"

    def test_equality(self):
        assert Kortti("♠", "A") == Kortti("♠", "A")

    def test_inequality(self):
        assert Kortti("♠", "A") != Kortti("♡", "A")


class TestKäsi:
    def test_oletusarvo_häviäjälle(self):
        """Häviäjän oletusarvo: muckasiko=True."""
        pelaaja = Pelaaja("Testi", 1)
        käsi = Käsi(pelaaja, [Kortti("♠", "A")])
        assert käsi.muckasiko is True
        assert käsi.voittiko is False

    def test_oletusarvo_voittajalle(self):
        """Voittajan sentinel-logiikka: muckasiko=False oletuksena."""
        pelaaja = Pelaaja("Testi", 1)
        käsi = Käsi(pelaaja, [Kortti("♠", "A")], voittiko=True)
        assert käsi.muckasiko is False

    def test_voittaja_voi_muckata(self):
        """Eksplisiittinen muckasiko=True voittajalla on sallittua (fold ennen showdownia)."""
        pelaaja = Pelaaja("Testi", 1)
        käsi = Käsi(pelaaja, [Kortti("♠", "A")], voittiko=True, muckasiko=True)
        assert käsi.muckasiko is True
        assert käsi.voittiko is True

    def test_häviäjä_voi_näyttää(self):
        """Häviäjä voi näyttää kätensä (muckasiko=False)."""
        pelaaja = Pelaaja("Testi", 1)
        käsi = Käsi(pelaaja, [Kortti("♠", "A")], voittiko=False, muckasiko=False)
        assert käsi.muckasiko is False


class TestEdellinenJako:
    def test_validointi_ilman_voittajaa(self, pelaajat):
        """EdellinenJako ilman voittajaa nostaa ValueError."""
        p1, p2, _ = pelaajat
        with pytest.raises(ValueError, match="voittaja"):
            EdellinenJako(
                poltetut=[],
                yhteiset=[],
                kädet=[
                    Käsi(p1, [Kortti("♠", "A")], voittiko=False),
                    Käsi(p2, [Kortti("♡", "K")], voittiko=False),
                ],
            )

    def test_validointi_voittajalla(self, perus_jako):
        """Validi jako ei nosta poikkeusta."""
        assert perus_jako is not None

    def test_split_pot_hyväksytään(self, split_pot_jako):
        """Kaksi voittajaa on validi tila."""
        voittajat = [k for k in split_pot_jako.kädet if k.voittiko]
        assert len(voittajat) == 2