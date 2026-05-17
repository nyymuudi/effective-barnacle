from dataclasses import dataclass
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
    paikka: int   # 0 = jakaja, 1 = pieni blindi jne.

@dataclass
class Käsi:
    pelaaja: Pelaaja
    kortit: List[Kortti]
    voittiko: bool = False
    muckasiko: bool | None = None

    def __post_init__(self):
        if self.muckasiko is None:
            # Oletus: voittaja näyttää, häviäjä muckaa
            self.muckasiko = not self.voittiko

@dataclass
class EdellinenJako:
    poltetut: List[Kortti]
    yhteiset: List[Kortti]
    kädet: List[Käsi]
    def __post_init__(self):
        if not any(k.voittiko for k in self.kädet):
            raise ValueError("Jaossa on oltava voittaja!")