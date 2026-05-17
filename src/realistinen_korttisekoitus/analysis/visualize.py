"""
Visualisoinnit sekoituksen tilastolliselle analyysille.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless-yhteensopiva — ei vaadi graafista ympäristöä
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from .metrics import laske_entropia, laske_total_variation_distance, yhteenveto


def piirra_heatmap(
    counts: np.ndarray,
    otsikko: str = "Korttipaikkajakauma",
    tallenna: str | None = None,
) -> None:
    frekvenssit = counts / counts.sum(axis=1, keepdims=True)
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(frekvenssit, aspect="auto", cmap="hot",
                   vmin=0, vmax=2 / counts.shape[0])
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
    riffle_arvot = sorted(konvergenssidata.keys())
    max_entropia = np.log2(list(konvergenssidata.values())[0].shape[0])

    entropiat = [laske_entropia(konvergenssidata[k]).mean() / max_entropia
                 for k in riffle_arvot]
    tvd_arvot = [laske_total_variation_distance(konvergenssidata[k]).mean()
                 for k in riffle_arvot]
    fy_entropia = laske_entropia(fy_counts).mean() / max_entropia
    fy_tvd = laske_total_variation_distance(fy_counts).mean()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    ax1.plot(riffle_arvot, entropiat, "o-", color="#2196F3", label="GSR")
    ax1.axhline(fy_entropia, color="#F44336", linestyle="--", label="Fisher-Yates")
    ax1.axhline(1.0, color="gray", linestyle=":", alpha=0.5, label="Teoreettinen max")
    ax1.set_title("Entropia (suhteellinen)")
    ax1.set_xlabel("Riffle-toistot")
    ax1.set_ylabel("H / H_max")
    ax1.set_ylim(0, 1.05)
    ax1.legend()
    ax1.grid(alpha=0.3)

    ax2.plot(riffle_arvot, tvd_arvot, "o-", color="#2196F3", label="GSR")
    ax2.axhline(fy_tvd, color="#F44336", linestyle="--", label="Fisher-Yates")
    ax2.axhline(0.0, color="gray", linestyle=":", alpha=0.5)
    ax2.set_title("Total Variation Distance")
    ax2.set_xlabel("Riffle-toistot")
    ax2.set_ylabel("TVD")
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.suptitle("GSR vs Fisher-Yates: konvergenssi uniformiin jakaumaan", fontsize=13)
    plt.tight_layout()
    if tallenna:
        plt.savefig(tallenna, dpi=150)
    plt.show()


def piirra_jakaumavertailu(
    jakaumavertailu: dict[str, np.ndarray],
    tallenna: str | None = None,
) -> None:
    """
    Laajennus 1: Vertaa kolmea leikkauspistejakaumaa TVD:n ja entropian mukaan.
    Fisher-Yates toimii referenssinä.
    """
    nimet = ["beta", "binomial", "uniform", "fisher_yates"]
    värit = {"beta": "#2196F3", "binomial": "#4CAF50",
              "uniform": "#FF9800", "fisher_yates": "#F44336"}
    max_entropia = np.log2(list(jakaumavertailu.values())[0].shape[0])

    tvd_arvot = {n: laske_total_variation_distance(jakaumavertailu[n]).mean()
                 for n in nimet}
    entropia_arvot = {n: laske_entropia(jakaumavertailu[n]).mean() / max_entropia
                      for n in nimet}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    x = range(len(nimet))
    ax1.bar(x, [tvd_arvot[n] for n in nimet],
            color=[värit[n] for n in nimet], alpha=0.85)
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(nimet)
    ax1.set_title("TVD per leikkauspistejakauma")
    ax1.set_ylabel("TVD keskiarvo (pienempi = parempi)")
    ax1.grid(axis="y", alpha=0.3)

    ax2.bar(x, [entropia_arvot[n] for n in nimet],
            color=[värit[n] for n in nimet], alpha=0.85)
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(nimet)
    ax2.set_title("Entropia per leikkauspistejakauma")
    ax2.set_ylabel("H / H_max (suurempi = parempi)")
    ax2.set_ylim(0.995, 1.001)
    ax2.grid(axis="y", alpha=0.3)

    plt.suptitle("Herkkyysanalyysi: leikkauspistejakauman vaikutus", fontsize=13)
    plt.tight_layout()
    if tallenna:
        plt.savefig(tallenna, dpi=150)
    plt.show()

    # Tekstiyhteenveto
    print(f"\n{'Jakauma':<15} {'TVD':>10} {'Entropia (suhde)':>18}")
    print("-" * 45)
    for n in nimet:
        print(f"{n:<15} {tvd_arvot[n]:>10.4f} {entropia_arvot[n]:>18.4f}")


def piirra_strategiavertailu(
    strategiavertailu: dict[str, dict[int, np.ndarray]],
    tallenna: str | None = None,
) -> None:
    """
    Laajennus 2: Konvergenssikäyrät keräysstrategioittain.
    Vastaa: vaikuttaako keräysjärjestys konvergenssiin?
    """
    värit = {"perus": "#2196F3", "voittaja_päälle": "#4CAF50"}
    riffle_arvot = sorted(list(strategiavertailu.values())[0].keys())
    max_entropia = np.log2(list(list(strategiavertailu.values())[0].values())[0].shape[0])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    for strategia, counts_per_riffle in strategiavertailu.items():
        tvd = [laske_total_variation_distance(counts_per_riffle[k]).mean()
               for k in riffle_arvot]
        entropia = [laske_entropia(counts_per_riffle[k]).mean() / max_entropia
                    for k in riffle_arvot]
        väri = värit.get(strategia, "gray")
        ax1.plot(riffle_arvot, tvd, "o-", color=väri, label=strategia)
        ax2.plot(riffle_arvot, entropia, "o-", color=väri, label=strategia)

    ax1.set_title("TVD konvergenssi strategioittain")
    ax1.set_xlabel("Riffle-toistot")
    ax1.set_ylabel("TVD keskiarvo")
    ax1.legend()
    ax1.grid(alpha=0.3)

    ax2.set_title("Entropia konvergenssi strategioittain")
    ax2.set_xlabel("Riffle-toistot")
    ax2.set_ylabel("H / H_max")
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.suptitle("Keräysstrategioiden vaikutus sekoituksen konvergenssiin", fontsize=13)
    plt.tight_layout()
    if tallenna:
        plt.savefig(tallenna, dpi=150)
    plt.show()


def piirra_yhteenveto_taulukko(
    gsr_counts: np.ndarray,
    fy_counts: np.ndarray,
    riffle_toistot: int = 4,
) -> None:
    gsr = yhteenveto(gsr_counts)
    fy = yhteenveto(fy_counts)
    print(f"\n{'Mittari':<30} {'GSR (' + str(riffle_toistot) + ' rifflellä)':>20} {'Fisher-Yates':>15}")
    print("-" * 67)
    print(f"{'Entropia (suhde max)':.<30} {gsr['entropia_suhde']:>20.4f} {fy['entropia_suhde']:>15.4f}")
    print(f"{'TVD keskiarvo':.<30} {gsr['tvd_keskiarvo']:>20.4f} {fy['tvd_keskiarvo']:>15.4f}")
    print(f"{'Bias p-arvo (mediaani)':.<30} {gsr['bias_p_mediaani']:>20.4f} {fy['bias_p_mediaani']:>15.4f}")
    print(f"{'Biased kortit (p<0.05)':.<30} {gsr['bias_merkittavia']:>20} {fy['bias_merkittavia']:>15}")


def piirra_profiilivertailu(
    profiilivertailu: dict[str, dict[int, np.ndarray]],
    fy_counts: np.ndarray | None = None,
    tallenna: str | None = None,
) -> None:
    """
    Human imperfection model: konvergenssikäyrät dealer-profiileittain.
    Vastaa: kuinka paljon inhimillinen epätarkkuus hidastaa konvergenssia?
    """
    värit = {
        "ideaali":     "#2196F3",
        "kokenut":     "#4CAF50",
        "aloittelija": "#FF5722",
    }
    riffle_arvot = sorted(list(profiilivertailu.values())[0].keys())
    max_entropia = np.log2(list(list(profiilivertailu.values())[0].values())[0].shape[0])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    for profiili, counts_per_riffle in profiilivertailu.items():
        tvd = [laske_total_variation_distance(counts_per_riffle[k]).mean()
               for k in riffle_arvot]
        entropia = [laske_entropia(counts_per_riffle[k]).mean() / max_entropia
                    for k in riffle_arvot]
        väri = värit.get(profiili, "gray")
        ax1.plot(riffle_arvot, tvd, "o-", color=väri, linewidth=2, label=profiili)
        ax2.plot(riffle_arvot, entropia, "o-", color=väri, linewidth=2, label=profiili)

    if fy_counts is not None:
        fy_tvd = laske_total_variation_distance(fy_counts).mean()
        fy_entropia = laske_entropia(fy_counts).mean() / max_entropia
        ax1.axhline(fy_tvd, color="gray", linestyle="--", linewidth=1.5, label="Fisher-Yates")
        ax2.axhline(fy_entropia, color="gray", linestyle="--", linewidth=1.5, label="Fisher-Yates")

    ax1.set_title("TVD konvergenssi profiileittain")
    ax1.set_xlabel("Riffle-toistot")
    ax1.set_ylabel("TVD keskiarvo")
    ax1.legend()
    ax1.grid(alpha=0.3)

    ax2.set_title("Entropia konvergenssi profiileittain")
    ax2.set_xlabel("Riffle-toistot")
    ax2.set_ylabel("H / H_max")
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.suptitle("Human Imperfection Model: dealer-profiilin vaikutus konvergenssiin",
                 fontsize=13)
    plt.tight_layout()
    if tallenna:
        plt.savefig(tallenna, dpi=150)
    plt.show()