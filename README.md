# Realistic Card Shuffle

A Python implementation of the **Gilbert–Shannon–Reeds (GSR) model** for card shuffling, simulating the deterministic physical properties of a real riffle shuffle — as opposed to Fisher-Yates, which produces uniformly random permutations directly.

## Background

Bayer & Diaconis (1992) formalized the GSR model: a deck is cut according to a binomial distribution and cards fall from either half with probability proportional to the remaining pile size. The process is deterministic in the sense that the outcome depends on physical parameters rather than pseudorandomness.

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

**After 7 riffles**, GSR becomes statistically indistinguishable from Fisher-Yates across all metrics. TVD converges to 0.028 and biased cards drop to zero — consistent with the theoretical result that 7 riffle shuffles suffice to approach the uniform distribution on 52-card decks.

## Installation

```bash
git clone git@github.com:nyymuudi/effective-barnacle.git
cd effective-barnacle
pip3 install -e .
```

### CLI

```bash
# Shuffle once
python3 -m realistinen_korttisekoitus.cli sekoita --riffle 7

# Run statistical analysis (10,000 iterations)
python3 -m realistinen_korttisekoitus.cli analyysi --riffle 4 --iteraatiot 10000

# Run with convergence analysis and save plots
python3 -m realistinen_korttisekoitus.cli analyysi --riffle 7 --tallenna results.png
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

| Strategy | Order | Description |
|---|---|---|
| `perus` (default) | burned → losers → winners → community | Standard dealer collection |
| `voittaja_päälle` | burned → losers → community → winners | Winner's hand collected last, on top |

```python
valmistele_pakka_seuraavaa_jakoa_varten(deal, keräys_strategia="voittaja_päälle")
```

## Running Tests

```bash
pip3 install pytest
pytest tests/ -v
```

## References

- Bayer, D. & Diaconis, P. (1992). *Trailing the Dovetail Shuffle to its Lair*. The Annals of Applied Probability, 2(2), 294–313.
- Diaconis, P., McGrath, M. & Pitman, J. (1995). *Riffle shuffles, cycles, and descents*. Combinatorica, 15(1), 11–29.

## License

MIT
