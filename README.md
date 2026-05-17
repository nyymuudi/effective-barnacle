# Realistinen korttisekoitus

GSR-malliin (Gilbert–Shannon–Reeds) perustuva korttien sekoitusalgoritmi, joka jäljittelee fyysisen sekoituksen deterministisiä ominaisuuksia — toisin kuin satunnaisia permutaatioita tuottava Fisher-Yates.

## Tausta

Bayer & Diaconis (1992) osoittivat, että ihmisen suorittama riffle-sekoitus noudattaa GSR-mallia: pakka leikataan binomijakauman mukaisesti ja kortit pudotetaan vuorotellen kummaltakin puolelta suhteessa pinon kokoon. Malli on deterministinen siinä mielessä, että tulos riippuu fyysisistä parametreista — ei pseudosatunnaisuudesta.

Tämä toteutus mallintaa täydellisen pokerikierroksen jälkeisen korttien keräys- ja sekoitussarjan:

1. **Keräys** — kortit noudetaan pöytäpaikan mukaisessa järjestyksessä
2. **Riffle-sekoitus** — GSR-mallin mukainen epätäydellinen sekoitus (oletus: 4 kertaa)
3. **Strip-sekoitus** — nipuittain tapahtuva järjestyksenkääntö riffle-sekoitusten välissä
4. **Leikkaus** — betajakaumalla painotettu leikkauskohta

## Asennus

```bash
git clone git@github.com:nyymuudi/effective-barnacle.git
cd effective-barnacle
pip3 install -e .
```

## Käyttö

```python
from realistinen_korttisekoitus.models import Kortti, Pelaaja, Käsi, EdellinenJako
from realistinen_korttisekoitus.engine import valmistele_pakka_seuraavaa_jakoa_varten

p1 = Pelaaja("Aapo", 1)
p2 = Pelaaja("Bertta", 2)

jako = EdellinenJako(
    poltetut=[Kortti("♣", "3"), Kortti("♢", "5"), Kortti("♠", "2")],
    yhteiset=[
        Kortti("♠", "J"), Kortti("♡", "10"), Kortti("♢", "2"),
        Kortti("♣", "9"), Kortti("♠", "4"),
    ],
    kädet=[
        Käsi(p1, [Kortti("♠", "A"), Kortti("♡", "K")], voittiko=True),
        Käsi(p2, [Kortti("♣", "7"), Kortti("♢", "8")]),
    ],
)

pakka = valmistele_pakka_seuraavaa_jakoa_varten(jako, riffle_toistot=4, tee_strip=True)
print(pakka)
```

### Komentorivi

```bash
python3 -m realistinen_korttisekoitus.cli --riffle 4
python3 -m realistinen_korttisekoitus.cli --riffle 7 --no-strip
```

## Rakenne

```
src/realistinen_korttisekoitus/
├── models.py    # Kortti, Pelaaja, Käsi, EdellinenJako
├── kerays.py    # Korttien keräyslogiikka jaon jälkeen
├── shuffle.py   # riffle_shuffle, strip_shuffle, leikkaa_pakka
├── engine.py    # Pääputki
└── cli.py       # Komentorivityökalu
```

## Testit

```bash
pip3 install pytest
pytest tests/ -v
```

## Viitteet

- Bayer, D. & Diaconis, P. (1992). *Trailing the Dovetail Shuffle to its Lair*. The Annals of Applied Probability.
- Diaconis, P., McGrath, M. & Pitman, J. (1995). *Riffle shuffles, cycles, and descents*. Combinatorica.

## Lisenssi

MIT