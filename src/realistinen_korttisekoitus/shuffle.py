import random

def riffle_shuffle(pakka: list) -> list:
    """GSR-mallin mukainen riffle-sekoitus."""
    n = len(pakka)
    # Leikkauskohdan jakauma likimain binomi(n, 0.5)
    # Käytetään betajakaumaa tuottamaan 0–1 välinen arvo, josta kerrotaan n
    # Yksinkertaisempi: random.randint(0, n) * 0.5 + satunnainen painotus
    # Tarkempi: binomijakauma random.choices:lla
    # Alla yksinkertainen mutta toimiva lähestymistapa:
    c = int(random.betavariate(2, 2) * n)  # symmetrinen, keskellä todennäköisemmin
    c = max(1, min(n-1, c))
    vasen = pakka[:c]
    oikea = pakka[c:]

    tulos = []
    i, j = 0, 0
    while i < len(vasen) or j < len(oikea):
        if i < len(vasen) and (j >= len(oikea) or random.random() < (len(vasen)-i) / (len(vasen)-i + len(oikea)-j)):
            tulos.append(vasen[i])
            i += 1
        else:
            tulos.append(oikea[j])
            j += 1
    return tulos

def strip_shuffle(pakka: list) -> list:
    """Ottaa 1-5 kortin nippuja pakan päältä ja pinoaa uuteen pakkaan."""
    jaljella = pakka[:]
    uusi = []
    while jaljella:
        nipun_koko = min(random.randint(1, 5), len(jaljella))
        nippu = jaljella[:nipun_koko]
        jaljella = jaljella[nipun_koko:]
        uusi = nippu + uusi  # kääntää järjestyksen
    return uusi

def leikkaa_pakka(pakka: list) -> list:
    n = len(pakka)
    c = int(random.betavariate(2, 2) * n)
    c = max(1, min(n-1, c))
    return pakka[c:] + pakka[:c]