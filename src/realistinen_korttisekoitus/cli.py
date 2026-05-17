import argparse
from .models import Kortti, Pelaaja, Käsi, EdellinenJako
from .engine import valmistele_pakka_seuraavaa_jakoa_varten


def _demo_jako() -> EdellinenJako:
    p1 = Pelaaja("Aapo", 1)
    p2 = Pelaaja("Bertta", 2)
    return EdellinenJako(
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


def cmd_sekoita(args) -> None:
    jako = _demo_jako()
    pakka = valmistele_pakka_seuraavaa_jakoa_varten(
        jako, args.riffle, args.strip, args.strategia, seed=args.seed
    )
    print("Sekoitettu pakka:", pakka)


def cmd_analyysi(args) -> None:
    from .analysis import (
        aja_simulaatio, aja_fisher_yates_simulaatio, aja_konvergenssianalyysi,
        aja_jakaumavertailu, aja_strategiavertailu,
        piirra_heatmap, piirra_konvergenssikayra, piirra_jakaumavertailu,
        piirra_strategiavertailu, piirra_yhteenveto_taulukko,
    )

    if args.jakaumavertailu:
        print(f"Ajetaan jakaumavertailu ({args.iteraatiot:,} iteraatiota, {args.riffle} rifflellä)...")
        data = aja_jakaumavertailu(n_iteraatiot=args.iteraatiot, riffle_toistot=args.riffle)
        piirra_jakaumavertailu(data, tallenna=args.tallenna)
        return

    if args.strategiavertailu:
        print(f"Ajetaan strategiavertailu ({args.iteraatiot:,} iteraatiota, 1–10 rifflellä)...")
        data = aja_strategiavertailu(n_iteraatiot=args.iteraatiot)
        piirra_strategiavertailu(data, tallenna=args.tallenna)
        return

    print(f"Ajetaan simulaatio ({args.iteraatiot:,} iteraatiota, {args.riffle} rifflellä)...")
    gsr = aja_simulaatio(n_iteraatiot=args.iteraatiot, riffle_toistot=args.riffle)
    fy = aja_fisher_yates_simulaatio(n_iteraatiot=args.iteraatiot)
    piirra_yhteenveto_taulukko(gsr, fy, riffle_toistot=args.riffle)

    if not args.ei_kuvia:
        piirra_heatmap(gsr, otsikko=f"GSR ({args.riffle} rifflellä)", tallenna=args.tallenna)
        piirra_heatmap(fy, otsikko="Fisher-Yates")
        print("Ajetaan konvergenssianalyysi (1–10 rifflellä)...")
        konv = aja_konvergenssianalyysi(n_iteraatiot=args.iteraatiot)
        piirra_konvergenssikayra(konv, fy, tallenna=args.tallenna)


def main():
    parser = argparse.ArgumentParser(description="Realistinen korttien sekoitussimulaatio")
    alikomennot = parser.add_subparsers(dest="komento")

    # sekoita
    p_sek = alikomennot.add_parser("sekoita", help="Sekoita pakka kerran")
    p_sek.add_argument("--riffle", type=int, default=4)
    p_sek.add_argument("--no-strip", action="store_false", dest="strip")
    p_sek.add_argument("--strategia", default="perus", choices=["perus", "voittaja_päälle"])

    # analyysi
    p_ana = alikomennot.add_parser("analyysi", help="Tilastollinen analyysi")
    p_ana.add_argument("--riffle", type=int, default=4)
    p_ana.add_argument("--iteraatiot", type=int, default=10_000)
    p_ana.add_argument("--ei-kuvia", action="store_true")
    p_ana.add_argument("--tallenna", type=str, default=None)
    p_ana.add_argument("--jakaumavertailu", action="store_true",
                       help="Vertaa beta/binomial/uniform leikkauspistejakaumia")
    p_ana.add_argument("--strategiavertailu", action="store_true",
                       help="Vertaa keräysstrategioiden konvergenssia")

    args = parser.parse_args()
    if args.komento == "sekoita":
        cmd_sekoita(args)
    elif args.komento == "analyysi":
        cmd_analyysi(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()