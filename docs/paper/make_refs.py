"""Write the reference list from metadata fetched from arXiv and Crossref."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
FETCHED = json.loads((HERE / "refs.json").read_text(encoding="utf-8"))
HAND = {
    "becguard": r"""A.~Cidon, L.~Gavish, I.~Bleier, N.~Korshun, M.~Schweighauser, and A.~Tsitkin, ``High precision detection of business email compromise,'' in \emph{Proc. 28th USENIX Security Symp.}, 2019, pp.~1291--1307.""",
    "phishllm": r"""R.~Liu, Y.~Lin, X.~Teoh, G.~Liu, Z.~Huang, and J.~S.~Dong, ``Less defined knowledge and more true alarms: Reference-based phishing detection without a pre-defined reference list,'' in \emph{Proc. USENIX Security Symp.}, 2024.""",
    "arp": r"""D.~Arp \emph{et al.}, ``Dos and don'ts of machine learning in computer security,'' in \emph{Proc. 31st USENIX Security Symp.}, 2022, pp.~3971--3988.""",
    "fire": r"""M.~Amjad \emph{et al.}, ``Overview of abusive and threatening language detection in Urdu at FIRE 2021,'' in \emph{Working Notes of FIRE 2021}, CEUR-WS Vol.~3159, 2021, pp.~744--762.""",
    "mhs": r"""P.~Sachdeva \emph{et al.}, ``The Measuring Hate Speech corpus: Leveraging Rasch measurement theory for data perspectivism,'' in \emph{Proc. 1st Workshop on Perspectivist Approaches to NLP}, 2022, pp.~83--94.""",
    "lightgbm": r"""G.~Ke \emph{et al.}, ``LightGBM: A highly efficient gradient boosting decision tree,'' in \emph{Proc. NeurIPS}, 2017.""",
    "mawi": r"""MAWI Working Group, ``MAWI working group traffic archive.'' [Online]. Available: \url{https://mawi.wide.ad.jp/mawi/}""",
    "darktrace": r"""Darktrace, ``Platform overview.'' [Online]. Available: \url{https://www.darktrace.com/platform}. Accessed: Nov. 6, 2026.""",
    "triage": r"""Microsoft, ``Phishing Triage Agent in Microsoft Defender.'' [Online]. Available: \url{https://learn.microsoft.com/en-us/defender-xdr/phishing-triage-agent}. Accessed: Nov. 6, 2026.""",
    "aisoc": r"""AiSOC project. [Online]. Available: \url{https://github.com/beenuar/AiSOC}. Accessed: Nov. 6, 2026.""",
    "slips": r"""Stratosphere Laboratory, ``Slips.'' [Online]. Available: \url{https://github.com/stratosphereips/StratosphereLinuxIPS}. Accessed: Nov. 6, 2026.""",
    "minilm": r"""Microsoft, ``Multilingual-MiniLM-L12-H384.'' [Online]. Available: \url{https://huggingface.co/microsoft/Multilingual-MiniLM-L12-H384}""",
    "code": r"""STL prototype, code and test sets. Link to be added at submission.""",
}


COMPOUND = {
    "Edir Garcia Lazo": "E.~Garcia~Lazo",
    "Victor Le Pochat": "V.~Le~Pochat",
    "Tom Van Goethem": "T.~Van~Goethem",
    "José María G. Hidalgo": "J.~M.~G.~Hidalgo",
}


def initials(name: str) -> str:
    if name in COMPOUND:
        return COMPOUND[name]
    parts = name.replace(".", ". ").split()
    if len(parts) == 1:
        return parts[0]
    given = "~".join(f"{part[0]}." for part in parts[:-1])
    return f"{given}~{parts[-1]}"


def authors(names: list[str]) -> str:
    short = [initials(name) for name in names]
    if len(short) > 6:
        return short[0] + r" \emph{et al.}"
    if len(short) == 1:
        return short[0]
    if len(short) == 2:
        return f"{short[0]} and {short[1]}"
    return ", ".join(short[:-1]) + f", and {short[-1]}"


def tidy(title: str) -> str:
    return title.replace("&", r"\&").replace("#", r"\#").replace("%", r"\%")


def clean_venue(venue: str) -> str:
    return tidy(venue.replace("&amp;", "&").strip())


def entry(key: str) -> str:
    if key in HAND:
        return HAND[key]
    item = FETCHED[key]
    title = tidy(item["title"])
    who = authors(item["authors"])
    if "arxiv" in item:
        return f"{who}, ``{title},'' arXiv:{item['arxiv']}, {item['year']}."
    venue = clean_venue(item.get("venue", ""))
    tail = f", vol.~{item['volume']}" if item.get("volume") else ""
    pages = f", pp.~{item['pages'].replace('-', '--')}" if item.get("pages") else ""
    style = r"\emph{" + venue + "}" if venue else ""
    return f"{who}, ``{title},'' {style}{tail}{pages}, {item['year']}, doi: {item['doi'].replace('_', chr(92) + '_')}."


def main() -> None:
    keys: list[str] = []
    for path in sorted((HERE / "sections").glob("*.tex"), key=lambda p: ("intro" not in p.name, p.name)):
        for group in re.findall(r"\\cite\{([^}]+)\}", path.read_text(encoding="utf-8")):
            for key in group.split(","):
                if key.strip() not in keys:
                    keys.append(key.strip())
    lines = [r"\begin{thebibliography}{99}"]
    for key in keys:
        lines.append(rf"\bibitem{{{key}}} {entry(key)}")
    lines.append(r"\end{thebibliography}")
    (HERE / "references.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(len(keys), "references")


if __name__ == "__main__":
    main()
