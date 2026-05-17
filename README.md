# Realistic Card Shuffle

![Tests](https://github.com/nyymuudi/effective-barnacle/actions/workflows/test.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A statistically grounded simulation of real-world card shuffling based on the Gilbert–Shannon–Reeds (GSR) riffle model. Unlike Fisher–Yates, which generates uniformly random permutations directly, this project models the physical shuffle process itself — including collection order, imperfect riffles, strip shuffles, and cuts.

## Key Insight

Even when using statistically strong riffle shuffling, the *collection order* from the previous hand leaves detectable structure in the deck for several shuffle rounds. This simulator models that hidden state explicitly — and measures it.

## Why This Matters

Realistic shuffle simulation has applications in:
- **Casino procedure analysis** — how many shuffles are actually needed?
- **Poker fairness research** — does collection order introduce measurable bias?
- **Shuffle bias visualization** — positional heatmaps reveal residual structure
- **Entropy convergence studies** — empirically verify theoretical mixing bounds
- **Game AI environments** — more realistic deck state modeling
- **Educational probability demonstrations** — GSR vs uniform randomness

## Background

Bayer & Diaconis (1992) formalized the GSR model: a deck is cut according to a binomial distribution and cards fall from either half with probability proportional to the remaining pile size. Unlike Fisher–Yates, the GSR model approximates the stochastic mechanics of real riffle shuffling, producing distributions that reflect physical constraints rather than uniform randomness.

This implementation models the full post-hand collection and shuffle sequence in a poker game:

1. **Collection** — cards are gathered in seat-order following a configurable strategy
2. **Riffle shuffle** — imperfect GSR-model riffle, repeated N times (default: 4)
3. **Strip shuffle** — packet-wise reversal interspersed between riffles
4. **Cut** — beta-distribution weighted cut point

## Empirical Findings

Running 10,000 Monte Carlo simulations confirms the Bayer & Diaconis result empirically:

| Metric | GSR (4 riffles) | GSR (7 riffles) | Fisher-Yates |
|---|---|---|---|
| Entropy (ratio to max) | 0.9991 | 0.9994 | 0.9994 |
| Total Variation Distance | 0.0327 | 0.0281 | 0.0280 |
| Bias p-value (median) | 0.2691 | 0.5105 | 0.5889 |
| Statistically biased cards (p<0.05) | 13 | 0 | 1 |

**After 4 riffles**, 13 cards show statistically significant positional bias — residual structure from the collection order remains detectable. This is the vulnerability Diaconis identified in casino contexts.

**After 7 riffles**, After 7 riffles, GSR approaches Fisher–Yates closely across all measured metrics. TVD converges to 0.028 and biased cards drop to zero — consistent with the theoretical result that 7 riffle shuffles suffice to approach the uniform distribution on 52-card decks.

> **Note:** TVD values are estimated empirically from finite samples (10,000 iterations). Fisher-Yates TVD ≈ 0.028 reflects estimation noise, not algorithmic bias.

<img width="2384" height="770" alt="image" src="https://github.com/user-attachments/assets/69f5e2e9-13bc-4108-b8a9-3b0cf968a734" />

### Collection Strategy Effect

Collection strategy has a measurable impact on convergence speed, but only at low riffle counts (1–3). After 4+ riffles, all strategies converge to equivalent TVD (~0.040).

| Strategy | TVD after 1 riffle | TVD after 4 riffles |
|---|---|---|
| `perus` | ~0.090 | ~0.040 |
| `voittaja_päälle` | ~0.091 | ~0.040 |
| `wash` | ~0.075 | ~0.041 |

The wash strategy disrupts collection-order structure more aggressively at the collection phase itself — reducing initial TVD by ~17% compared to standard collection. This advantage disappears after sufficient riffling, but is practically relevant in casino contexts where dealers typically perform only 3–4 shuffles between hands.

## Research Notes

This simulator approximates real-world shuffling behavior but does not
attempt to model all biomechanical properties of human dealers.

The implementation focuses on:
- probabilistic riffle interleaving,
- collection-order persistence,
- imperfect cuts,
- and convergence behavior under repeated shuffling.

Results are empirical and depend on:
- iteration count,
- chosen metrics,
- and shuffle parameterization.

## Installation

```bash
git clone git@github.com:nyymuudi/effective-barnacle.git
cd effective-barnacle
pip3 install -e .
```

## Usage

### Python API

```python
from realistinen_korttisekoitus.models import Kortti, Pelaaja, Käsi, EdellinenJako
from realistinen_korttisekoitus.engine import valmistele_pakka_seuraavaa_jakoa_varten

p1 = Pelaaja("Alice", 1)
p2 = Pelaaja("Bob", 2)

deal = EdellinenJako(
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

# Reproducible result with seed
deck = valmistele_pakka_seuraavaa_jakoa_varten(deal, riffle_toistot=7, seed=42)
```

### CLI

```bash
# Shuffle once
python3 -m realistinen_korttisekoitus.cli sekoita --riffle 7

# Reproducible shuffle with seed
python3 -m realistinen_korttisekoitus.cli sekoita --riffle 7 --seed 42

# Run statistical analysis (10,000 iterations)
python3 -m realistinen_korttisekoitus.cli analyysi --riffle 4 --iteraatiot 10000

# Compare cut-point distributions (beta vs binomial vs uniform)
python3 -m realistinen_korttisekoitus.cli analyysi --jakaumavertailu

# Compare collection strategies
python3 -m realistinen_korttisekoitus.cli analyysi --strategiavertailu
```

## Project Structure

```
src/realistinen_korttisekoitus/
├── models.py        # Kortti, Pelaaja, Käsi, EdellinenJako
├── kerays.py        # Collection logic and strategies
├── shuffle.py       # riffle_shuffle, strip_shuffle, leikkaa_pakka
├── engine.py        # Main pipeline
├── cli.py           # Command-line interface
└── analysis/
    ├── montecarlo.py  # Simulation runner
    ├── metrics.py     # Entropy, TVD, permutation bias
    └── visualize.py   # Heatmaps, convergence curves
```

## Collection Strategies

Two strategies are available for the post-hand card collection phase:

| Strategy          | Order                                 | Description                                                                                        |
| ----------------- | ------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `perus` (default) | burned → losers → winners → community | Standard dealer collection                                                                         |
| `voittaja_päälle` | burned → losers → community → winners | Winner's hand collected last, on top                                                               |
| `wash`            | scrambled groups                      | Cards spread on table and randomly regrouped — breaks collection-order structure most aggressively |

```python
valmistele_pakka_seuraavaa_jakoa_varten(deal, keräys_strategia="voittaja_päälle")
```

## Running Tests

```bash
pip3 install pytest
pytest tests/ -v
```

## References

- Bayer, D. & Diaconis, P. (1992). *Trailing the Dovetail Shuffle to its Lair*. The Annals of Applied Probability, 2(2), 294–313. https://doi.org/10.1214/aoap/1177005705
- Diaconis, P., McGrath, M. & Pitman, J. (1995). *Riffle shuffles, cycles, and descents*. Combinatorica, 15(1), 11–29.

## License

MIT
