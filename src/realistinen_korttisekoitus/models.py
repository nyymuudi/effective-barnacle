from dataclasses import dataclass, field
from typing import List


@dataclass
class Kortti:
    maa: str
    arvo: str
    def __repr__(self) -> str:
        return f"{self.arvo}{self.maa}"


@dataclass
class Pelaaja:
    nimi: str
    paikka: int


@dataclass
class Käsi:
    pelaaja: Pelaaja
    kortit: list[Kortti]
    voittiko: bool = False
    muckasiko: bool | None = None

    def __post_init__(self):
        if self.muckasiko is None:
            self.muckasiko = not self.voittiko


@dataclass
class EdellinenJako:
    poltetut: list[Kortti]
    yhteiset: list[Kortti]
    kädet: list[Käsi]

    def __post_init__(self):
        if not any(k.voittiko for k in self.kädet):
            raise ValueError("Jaossa on oltava voittaja!")


@dataclass
class DealerProfiili:
    """
    Mallintaa dealerin inhimillistä epätarkkuutta rifflen aikana.

    Parametrit:
        nimi:                 Profiilin tunniste.
        dominant_hand_bias:   Leikkauspisteen vinoutuma. 0.5 = täydellinen keskileikkaus,
                              >0.5 = oikea käsi dominoi (leikkaus yli puolivälin).
        clump_probability:    Todennäköisyys että kortti "klumppautuu" — putoaa pareittain
                              edellisen kortin kanssa samasta puoliskosta.
        pressure_variance:    Hajonta rifflen pudotustodennäköisyydessä. Kuvaa epätasaista
                              sormipainetta: korkea arvo = pitkiä juoksuja yhdestä puoliskosta.
        strip_irregularity:   Strip-nipun koon hajonta. Korkea arvo = hyvin epätasaiset niput.
    """
    nimi: str
    dominant_hand_bias: float = 0.5
    clump_probability: float = 0.0
    pressure_variance: float = 0.05
    strip_irregularity: float = 0.3


# Valmiit arkkityypit
DEALER_PROFIILIT: dict[str, DealerProfiili] = {
    "ideaali": DealerProfiili(
        nimi="Ideaali",
        dominant_hand_bias=0.5,
        clump_probability=0.0,
        pressure_variance=0.05,
        strip_irregularity=0.3,
    ),
    "kokenut": DealerProfiili(
        nimi="Kokenut",
        dominant_hand_bias=0.52,
        clump_probability=0.05,
        pressure_variance=0.10,
        strip_irregularity=0.5,
    ),
    "aloittelija": DealerProfiili(
        nimi="Aloittelija",
        dominant_hand_bias=0.58,
        clump_probability=0.15,
        pressure_variance=0.20,
        strip_irregularity=1.0,
    ),
}