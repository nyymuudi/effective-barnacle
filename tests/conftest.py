"""
Jaetut pytest-fixturet kaikille testeille.
"""
import pytest
from realistinen_korttisekoitus.models import Kortti, Pelaaja, Käsi, EdellinenJako

MAAt = ["♠", "♡", "♢", "♣"]
ARVOt = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


@pytest.fixture
def täysi_pakka() -> list[Kortti]:
    """Standardi 52 kortin pakka."""
    return [Kortti(maa, arvo) for maa in MAAt for arvo in ARVOt]


@pytest.fixture
def pelaajat() -> list[Pelaaja]:
    return [
        Pelaaja("Aapo", 1),
        Pelaaja("Bertta", 2),
        Pelaaja("Cecilia", 3),
    ]


@pytest.fixture
def perus_jako(pelaajat) -> EdellinenJako:
    """Tyypillinen jako: 3 pelaajaa, yksi voittaja, yksi showdown, yksi muckaus."""
    p1, p2, p3 = pelaajat
    return EdellinenJako(
        poltetut=[
            Kortti("♣", "3"),
            Kortti("♢", "5"),
            Kortti("♠", "2"),
        ],
        yhteiset=[
            Kortti("♠", "J"),
            Kortti("♡", "10"),
            Kortti("♢", "2"),
            Kortti("♣", "9"),
            Kortti("♠", "4"),
        ],
        kädet=[
            Käsi(p1, [Kortti("♠", "A"), Kortti("♡", "K")], voittiko=True),
            Käsi(p2, [Kortti("♣", "7"), Kortti("♢", "8")], muckasiko=False),  # näytti käden
            Käsi(p3, [Kortti("♡", "Q"), Kortti("♠", "10")]),                  # muckasi
        ],
    )


@pytest.fixture
def split_pot_jako(pelaajat) -> EdellinenJako:
    """Jako jossa kaksi voittajaa (split pot)."""
    p1, p2, p3 = pelaajat
    return EdellinenJako(
        poltetut=[Kortti("♣", "3")],
        yhteiset=[
            Kortti("♠", "J"), Kortti("♡", "10"), Kortti("♢", "2"),
            Kortti("♣", "9"), Kortti("♠", "4"),
        ],
        kädet=[
            Käsi(p1, [Kortti("♠", "A"), Kortti("♡", "A")], voittiko=True),
            Käsi(p2, [Kortti("♣", "A"), Kortti("♢", "A")], voittiko=True),
            Käsi(p3, [Kortti("♡", "Q"), Kortti("♠", "10")]),
        ],
    )


@pytest.fixture
def voittaja_muckasi_jako(pelaajat) -> EdellinenJako:
    """Voittaja ei näytä korttejaan (vastustajat foldasivat)."""
    p1, p2 = pelaajat[:2]
    return EdellinenJako(
        poltetut=[Kortti("♣", "3")],
        yhteiset=[
            Kortti("♠", "J"), Kortti("♡", "10"), Kortti("♢", "2"),
            Kortti("♣", "9"), Kortti("♠", "4"),
        ],
        kädet=[
            Käsi(p1, [Kortti("♠", "A"), Kortti("♡", "K")], voittiko=True, muckasiko=True),
            Käsi(p2, [Kortti("♣", "7"), Kortti("♢", "8")]),
        ],
    )