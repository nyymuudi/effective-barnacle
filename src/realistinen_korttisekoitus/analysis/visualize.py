"""
Visualisoinnit sekoituksen tilastolliselle analyysille.

  - Korttipaikkajakauman heatmap
  - Entropian konvergenssikäyrä riffle-toistomäärän funktiona
  - GSR vs Fisher-Yates TVD-vertailu
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from .metrics import laske_entropia, laske_total_variation_distance, yhteenveto


def piirra_heatmap(
    counts: np.ndarray,
    otsikko: str = "Korttipaikkajakauma",
    tallenna: str | None = None,
) -> None:
    """
    Heatmap: rivi = kortti, sarake = loppupaikka.
    Täydellinen sekoitus näyttää tasaisen harmaan (kaikki frekvenssit ~1/n).
    """
    frekvenssit = counts / counts.sum(axis=1, keepdims=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(frekvenssit, aspect="auto", cmap="hot", vmin=0, vmax=2 / counts.shape[0])
    fig.colorbar(im, ax=ax, label="Frekvenssi")

    ax.set_title(otsikko, fontsize=14)
    ax.set_xlabel("Loppupaikka")
    ax.set_ylabel("Kortti (alkuperäinen järjestys)")
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(10))

    plt.tight_layout()
    if tallenna:
        plt.savefig(tallenna, dpi=150)
    plt.show()


def piirra_konvergenssikayra(
    konvergenssidata: dict[int, np.ndarray],
    fy_counts: np.ndarray,
    tallenna: str | None = None,
) -> None:
    """
    Entropian ja TVD:n konvergenssikäyrä riffle-toistomäärän funktiona.
    Piirtää GSR-käyrän ja Fisher-Yates referenssiviivan.
    """
    riffle_arvot = sorted(konvergenssidata.keys())
    max_entropia = np.log2(list(konvergenssidata.values())[0].shape[0])

    entropiat = [
        laske_entropia(konvergenssidata[k]).mean() / max_entropia
        for k in riffle_arvot
    ]
    tvd_arvot = [
        laske_total_variation_distance(konvergenssidata[k]).mean()
        for k in riffle_arvot
    ]

    fy_entropia = laske_entropia(fy_counts).mean() / max_entropia
    fy_tvd = laske_total_variation_distance(fy_counts).mean()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Entropia
    ax1.plot(riffle_arvot, entropiat, "o-", color="#2196F3", label="GSR")
    ax1.axhline(fy_entropia, color="#F44336", linestyle="--", label="Fisher-Yates")
    ax1.axhline(1.0, color="gray", linestyle=":", alpha=0.5, label="Teoreettinen max")
    ax1.set_title("Entropia (suhteellinen)")
    ax1.set_xlabel("Riffle-toistot")
    ax1.set_ylabel("H / H_max")
    ax1.set_ylim(0, 1.05)
    ax1.legend()
    ax1.grid(alpha=0.3)

    # TVD
    ax2.plot(riffle_arvot, tvd_arvot, "o-", color="#2196F3", label="GSR")
    ax2.axhline(fy_tvd, color="#F44336", linestyle="--", label="Fisher-Yates")
    ax2.axhline(0.0, color="gray", linestyle=":", alpha=0.5, label="Teoreettinen min")
    ax2.set_title("Total Variation Distance")
    ax2.set_xlabel("Riffle-toistot")
    ax2.set_ylabel("TVD (0 = uniform)")
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.suptitle("GSR vs Fisher-Yates: konvergenssi uniformiin jakaumaan", fontsize=13)
    plt.tight_layout()
    if tallenna:
        plt.savefig(tallenna, dpi=150)
    plt.show()


def piirra_yhteenveto_taulukko(
    gsr_counts: np.ndarray,
    fy_counts: np.ndarray,
    riffle_toistot: int = 4,
) -> None:
    """
    Tulostaa tekstimuotoisen yhteenvetotaulukon konsoliin.
    """
    gsr = yhteenveto(gsr_counts)
    fy = yhteenveto(fy_counts)

    print(f"\n{'Mittari':<30} {'GSR (' + str(riffle_toistot) + ' rifflellä)':>20} {'Fisher-Yates':>15}")
    print("-" * 67)
    print(f"{'Entropia (suhde max)':.<30} {gsr['entropia_suhde']:>20.4f} {fy['entropia_suhde']:>15.4f}")
    print(f"{'TVD keskiarvo':.<30} {gsr['tvd_keskiarvo']:>20.4f} {fy['tvd_keskiarvo']:>15.4f}")
    print(f"{'Bias p-arvo (mediaani)':.<30} {gsr['bias_p_mediaani']:>20.4f} {fy['bias_p_mediaani']:>15.4f}")
    print(f"{'Biased kortit (p<0.05)':.<30} {gsr['bias_merkittavia']:>20} {fy['bias_merkittavia']:>15}")