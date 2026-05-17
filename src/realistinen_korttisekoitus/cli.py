import argparse
from .models import Kortti, Pelaaja, Käsi, EdellinenJako
from .engine import valmistele_pakka_seuraavaa_jakoa_varten

def main():
    parser = argparse.ArgumentParser(description="Realistinen korttien sekoitussimulaatio")
    parser.add_argument("--riffle", type=int, default=4, help="Riffle-sekoitusten määrä")
    parser.add_argument("--no-strip", action="store_false", dest="strip")
    args = parser.parse_args()

    # Esimerkki edellisestä jaosta
    p1 = Pelaaja("Aapo", 1)
    p2 = Pelaaja("Bertta", 2)
    jako = EdellinenJako(
        poltetut=[Kortti("♣", "3")],
        yhteiset=[Kortti("♠", "J"), Kortti("♡", "10"), Kortti("♢", "2")],
        kädet=[
            Käsi(p1, [Kortti("♠", "A"), Kortti("♡", "K")], voittiko=True),
            Käsi(p2, [Kortti("♣", "7"), Kortti("♢", "8")]),
        ]
    )
    uusi_pakka = valmistele_pakka_seuraavaa_jakoa_varten(jako, args.riffle, args.strip)
    print("Sekoitettu pakka:", uusi_pakka)

if __name__ == "__main__":
    main()