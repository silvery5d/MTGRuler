"""Enumerate all CR versions available from Academy Ruins.

Two strategies combined:
1. Walk the diff-chain backward from latest (covers ~2017-present with nav links)
2. Probe known historical set codes directly via /file/cr/{code} (covers 1999-2017)
"""

import json
from pathlib import Path

import httpx

from .fetch import fetch_diff, fetch_latest_diff_with_nav, fetch_cr_text, _get_client, DATA_DIR

VERSIONS_INDEX = DATA_DIR / "versions_index.json"

# All known MTG versions in chronological order.
# Pre-CR era (narrative rulebooks) from hudecekpetr.cz archive.
# CR era (6ED onward) from Academy Ruins (verified via HTTP 200 probes).
KNOWN_PRE_AKH_SETS: list[tuple[str, str, str | None]] = [
    # Pre-CR narrative rulebooks (fetched from hudecekpetr.cz)
    ("ALPHA", "Alpha / Beta Rulebook", "1993-08-05"),
    ("UNLIMITED", "Unlimited Rulebook", "1993-12-01"),
    ("REVISED", "Revised Edition Rulebook", "1994-04-01"),
    ("5TH", "Fifth Edition Rulebook", "1997-03-01"),
    # Comprehensive Rules era
    ("6ED", "Classic Sixth Edition", "1999-04-28"),
    ("APC", "Apocalypse", "2001-06-04"),
    ("ODY", "Odyssey", "2001-10-01"),
    ("TOR", "Torment", "2002-02-04"),
    ("ONS", "Onslaught", "2002-10-07"),
    ("LGN", "Legions", "2003-02-03"),
    ("SCG", "Scourge", "2003-05-26"),
    ("8ED", "Eighth Edition", "2003-07-28"),
    ("MRD", "Mirrodin", "2003-10-02"),
    ("DST", "Darksteel", "2004-02-06"),
    ("5DN", "Fifth Dawn", "2004-06-04"),
    ("CHK", "Champions of Kamigawa", "2004-10-01"),
    ("BOK", "Betrayers of Kamigawa", "2005-02-04"),
    ("9ED", "Ninth Edition", "2005-07-29"),
    ("RAV", "Ravnica", "2005-10-07"),
    ("GPT", "Guildpact", "2006-02-03"),
    ("DIS", "Dissension", "2006-05-05"),
    ("CSP", "Coldsnap", "2006-07-21"),
    ("TSP", "Time Spiral", "2006-10-06"),
    ("PLC", "Planar Chaos", "2007-02-02"),
    ("FUT", "Future Sight", "2007-05-04"),
    ("10E", "Tenth Edition", "2007-07-13"),
    ("LRW", "Lorwyn", "2007-10-12"),
    ("MOR", "Morningtide", "2008-02-01"),
    ("SHM", "Shadowmoor", "2008-05-02"),
    ("EVE", "Eventide", "2008-07-25"),
    ("ALA", "Shards of Alara", "2008-10-03"),
    ("CON", "Conflux", "2009-02-06"),
    ("ARB", "Alara Reborn", "2009-04-30"),
    ("M10", "Magic 2010", "2009-07-17"),
    ("ZEN", "Zendikar", "2009-10-02"),
    ("WWK", "Worldwake", "2010-02-05"),
    ("ROE", "Rise of the Eldrazi", "2010-04-23"),
    ("M11", "Magic 2011", "2010-07-16"),
    ("SOM", "Scars of Mirrodin", "2010-10-01"),
    ("MBS", "Mirrodin Besieged", "2011-02-04"),
    ("NPH", "New Phyrexia", "2011-05-13"),
    ("M12", "Magic 2012", "2011-07-15"),
    ("ISD", "Innistrad", "2011-09-30"),
    ("DKA", "Dark Ascension", "2012-02-03"),
    ("AVR", "Avacyn Restored", "2012-05-04"),
    ("M13", "Magic 2013", "2012-07-13"),
    ("RTR", "Return to Ravnica", "2012-10-05"),
    ("GTC", "Gatecrash", "2013-02-01"),
    ("DGM", "Dragon's Maze", "2013-05-03"),
    ("M14", "Magic 2014", "2013-07-19"),
    ("THS", "Theros", "2013-09-27"),
    ("BNG", "Born of the Gods", "2014-02-07"),
    ("JOU", "Journey into Nyx", "2014-05-02"),
    ("M15", "Magic 2015", "2014-07-18"),
    ("KTK", "Khans of Tarkir", "2014-09-26"),
    ("FRF", "Fate Reforged", "2015-01-23"),
    ("DTK", "Dragons of Tarkir", "2015-03-27"),
    ("ORI", "Magic Origins", "2015-07-17"),
    ("BFZ", "Battle for Zendikar", "2015-10-02"),
    ("OGW", "Oath of the Gatewatch", "2016-01-22"),
    ("SOI", "Shadows over Innistrad", "2016-04-08"),
    ("EMN", "Eldritch Moon", "2016-07-22"),
    ("KLD", "Kaladesh", "2016-09-30"),
    ("AER", "Aether Revolt", "2017-01-20"),
]


def walk_all_versions(max_steps: int = 200) -> list[dict]:
    """Enumerate all CR versions: pre-AKH from known list + AKH onward from diff chain.

    Returns chronological list (oldest first).
    """
    # Phase 1: walk diff chain backward from latest (AKH → present)
    latest = fetch_latest_diff_with_nav()
    chain: list[dict] = []

    current = {
        "set_code": latest["destCode"],
        "set_name": latest["destSet"],
        "release_date": latest.get("creationDay"),
        "prev_set_code": latest["sourceCode"],
        "next_set_code": None,
    }
    chain.append(current)

    chain.append({
        "set_code": latest["sourceCode"],
        "set_name": latest["sourceSet"],
        "release_date": None,
        "prev_set_code": latest.get("nav", {}).get("prevSourceCode"),
        "next_set_code": latest["destCode"],
    })

    steps = 0
    while chain[-1]["prev_set_code"] and steps < max_steps:
        prev_code = chain[-1]["prev_set_code"]
        curr_code = chain[-1]["set_code"]
        try:
            diff = fetch_diff(prev_code, curr_code)
        except (ValueError, Exception):
            break

        chain[-1]["release_date"] = diff.get("creationDay")
        chain.append({
            "set_code": diff["sourceCode"],
            "set_name": diff["sourceSet"],
            "release_date": None,
            "prev_set_code": diff.get("nav", {}).get("prevSourceCode"),
            "next_set_code": curr_code,
        })
        steps += 1

    chain.reverse()
    chain_codes = {v["set_code"] for v in chain}

    # Phase 2: prepend pre-AKH versions from known list (skip any already in chain)
    pre_chain: list[dict] = []
    for code, name, date in KNOWN_PRE_AKH_SETS:
        if code not in chain_codes:
            pre_chain.append({
                "set_code": code,
                "set_name": name,
                "release_date": date,
                "prev_set_code": None,
                "next_set_code": None,
            })

    # Combine: pre_chain + chain
    full = pre_chain + chain

    # Fix prev/next pointers
    for i in range(len(full)):
        full[i]["prev_set_code"] = full[i - 1]["set_code"] if i > 0 else None
        full[i]["next_set_code"] = full[i + 1]["set_code"] if i < len(full) - 1 else None

    VERSIONS_INDEX.parent.mkdir(parents=True, exist_ok=True)
    VERSIONS_INDEX.write_text(json.dumps(full, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Enumerated {len(full)} versions: {full[0]['set_code']} ({full[0].get('release_date','?')}) → {full[-1]['set_code']} ({full[-1].get('release_date','?')})")
    return full


def load_versions_index() -> list[dict]:
    """Load the cached versions index, or enumerate fresh if missing."""
    if VERSIONS_INDEX.exists():
        return json.loads(VERSIONS_INDEX.read_text(encoding="utf-8"))
    return walk_all_versions()
