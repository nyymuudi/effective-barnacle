from .kerays import kerää_kortit
from .shuffle import riffle_shuffle, strip_shuffle, leikkaa_pakka

def valmistele_pakka_seuraavaa_jakoa_varten(edellinen, riffle_toistot=4, tee_strip=True):
    pakka = kerää_kortit(edellinen)
    for i in range(riffle_toistot):
        pakka = riffle_shuffle(pakka)
        if tee_strip and i == 1:
            pakka = strip_shuffle(pakka)
    pakka = leikkaa_pakka(pakka)
    return pakka