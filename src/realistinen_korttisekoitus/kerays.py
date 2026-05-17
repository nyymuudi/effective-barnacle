from .models import EdellinenJako, Kortti

def kerää_kortit(jako: EdellinenJako) -> list:
    pakka = []
    # Poltetut pohjalle
    pakka.extend(jako.poltetut)
    
    # Muckatut kädet paikan mukaan
    ei_voittajat = [k for k in jako.kädet if not k.voittiko]
    ei_voittajat.sort(key=lambda k: k.pelaaja.paikka)
    for kasi in ei_voittajat:
        pakka.extend(kasi.kortit)
    
    # Voittajan käsi viimeiseksi
    for kasi in jako.kädet:
        if kasi.voittiko:
            pakka.extend(kasi.kortit)
    
    # Yhteiset kortit viimeiseksi (jäävät pakan päälle)
    pakka.extend(jako.yhteiset)
    return pakka