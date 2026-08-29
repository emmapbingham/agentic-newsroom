#!/usr/bin/env python3
"""Build the deduplicated APRA/ADPPA Senate client roster under E7's corrected
method (E7 in evidence.md).

E1/E5/E6 restricted to general_issue_code = 'CPI', which undercounts badly --
APRA/ADPPA is disclosed under 15+ issue codes (Consumer Issues/CSP alone has
more matching activity than CPI). This script uses E7's corrected filter
instead: any issue code, but length(description) < 600 to exclude the
omnibus multi-bill laundry-list filings that make a naive unrestricted match
overcount (some filers' description field runs to 20,000+ characters listing
50+ unrelated bills, with the APRA/ADPPA mention buried once inside).

That produces 399 raw distinct client names (derived/roster_corrected_any_
issue_code.csv). This script manually collapses the known name/entity
variants in that list (found by reading all 399 names once) the same way
build_roster.py did for E5's smaller 84-name CPI-only list, and writes
derived/roster_corrected_deduplicated.csv.

Re-run: python3 investigations/apra-lobbying-coalition/analysis/build_corrected_roster.py
Requires db/gain.db (read-only).
"""
import csv
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[3] / "db" / "gain.db"
OUT = Path(__file__).resolve().parent.parent / "derived" / "roster_corrected_deduplicated.csv"

QUERY = """
SELECT c.name,
       count(*) n_activities,
       count(DISTINCT sf.filing_uuid) n_filings,
       count(DISTINCT c.id) n_client_ids,
       min(sf.filing_year) first_year,
       max(sf.filing_year) last_year
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
JOIN senate_clients c ON c.id = sf.client_id
WHERE length(sla.description) < 600
  AND (
    lower(sla.description) LIKE '%american privacy rights act%'
    OR lower(sla.description) LIKE '%consumer online privacy rights act%'
    OR lower(sla.description) LIKE '%american data privacy%'
    OR lower(sla.description) LIKE '%adppa%'
  )
GROUP BY c.name
ORDER BY n_activities DESC;
"""

# Manually identified name/entity variants in the 399-raw-name corrected
# roster (found by reading the full list once). Only true same-registrant
# name-string variants are merged (different punctuation, corporate suffix,
# "formerly"/"fka" aliases, spelled-out vs abbreviated). Parent/subsidiary
# relationships (e.g. Credit Karma / Intuit) are NOT merged -- they are
# separately named, separately disclosed filers, consistent with E5's
# convention of only collapsing string-level duplicates of the same entity.
NAME_GROUPS = {
    "RELX": ["RELX INC.", "RELX INC"],
    "BLOCK": ["BLOCK, INC.", "BLOCK INC."],
    "MATCH GROUP": ["MATCH GROUP", "MATCH GROUP, LLC", "MATCH GROUP, INC."],
    "BSA / SOFTWARE ALLIANCE": [
        "BSA, THE SOFTWARE ALLIANCE",
        "BUSINESS SOFTWARE ALLIANCE",
        "BSA THE SOFTWARE ALLIANCE (FORMERLY BSA BUSINESS SOFTWARE ALLIANCE INC)",
    ],
    "TECHNET": ["TECHNET", "TECHNOLOGY NETWORK AKA TECHNET"],
    "INTUIT": [
        "INTUIT, INC. AND AFFILIATES (FORMERLY INTUIT, INC.)",
        "INTUIT, INC. AND AFFILIATES",
        "INTUIT, INC. AND AFFILIATES (F.K.A. INTUIT, INC.)",
    ],
    "META PLATFORMS": [
        "META PLATFORMS, INC.",
        "META PLATFORMS, INC. AND VARIOUS SUBSIDIARIES",
    ],
    "YAHOO": [
        'YAHOO INC, AND VAR. SUBS/AFFILIATES (FKA COLLEGE PARENT, L.P. DBA "YAHOO")',
        "YAHOO INC. AND VAR. SUBS/AFFILIATES",
    ],
    "LIVERAMP": ["LIVERAMP, INC.", "LIVERAMP HOLDINGS INC."],
    "SIIA": [
        "SOFTWARE & INFORMATION INDUSTRY ASSOCIATION",
        "SOFTWARE & INFORMATION INDUSTRY ASSOCIATION (SIIA)",
    ],
    "IBM": ["INTERNATIONAL BUSINESS MACHINES CORPORATION (IBM)", "IBM"],
    "DIRECTV": ["DIRECTV, LLC", "DIRECTV"],
    "SAP AMERICA": ["SAP AMERICA INC.", "SAP AMERICA, INC."],
    "TNC (US) HOLDINGS (FKA NIELSEN)": [
        "TNC (US) HOLDINGS INC",
        "TNC (US) HOLDINGS, INC. (FORMERLY NIELSEN)",
    ],
    "BUSINESS ROUNDTABLE": [
        "THE BUSINESS ROUNDTABLE",
        "BUSINESS ROUNDTABLE INC",
        "BUSINESS ROUNDTABLE",
    ],
    "AMERICAN HONDA MOTOR": [
        "AMERICAN HONDA MOTOR CO., INC.",
        "AMERICAN HONDA MOTOR CO INC (FORMERLY HONDA NORTH AMERICA)",
    ],
    "SENTRY INSURANCE": [
        "SENTRY INSURANCE COMPANY (FORMERLY SENTRY INSURANCE A MUTUAL COMPANY)",
        "SENTRY INSURANCE COMPANY",
    ],
    "AMAZON.COM SERVICES": ["AMAZON.COM SERVICES LLC", "AMAZON.COM SERVICES, INC."],
    "APPLE": ["APPLE INC.", "APPLE INC"],
    "REINSURANCE ASSOCIATION OF AMERICA": [
        "REINSURANCE ASSOCIATION OF AMERICA",
        "REINSURANCE ASSN OF AMERICA",
    ],
    "CHUBB INA HOLDINGS": [
        "CHUBB INA HOLDING COMPANY INC",
        "CHUBB INA HOLDINGS, INC.",
    ],
    "GOOGLE CLIENT SERVICES": [
        "GOOGLE CLIENT SERVICES LLC",
        "GOOGLE CLIENT SERVICES, LLC",
    ],
    "EBAY": ["EBAY INC.", "EBAY INC"],
    "YUM! BRANDS": ["YUM! BRANDS INC", "YUM! BRANDS"],
    "INFORMATION TECHNOLOGY INDUSTRY COUNCIL": [
        "INFORMATION TECHNOLOGY INDUSTRY COUNCIL",
        "INFORMATION TECHNOLOGY INDUSTRY COUNCIL (ITI)",
    ],
    "RETAIL INDUSTRY LEADERS ASSOCIATION": [
        "RETAIL INDUSTRY LEADERS ASSOCIATION",
        "RETAIL INDUSTRY LEADERS ASSOCIATION (RILA)",
    ],
    "AMERICAN PROPERTY CASUALTY INSURANCE ASSOCIATION": [
        "AMERICAN PROPERTY CASUALTY INSURANCE ASSOCIATION",
        "AMERICAN PROPERTY CASUALTY INSURANCE ASSOCIATION FKA PROPERTY CASUALTY INSURERS",
    ],
    "TWILIO": ["TWILIO, INC.", "TWILIO INC."],
    "AT&T SERVICES": [
        "AT&T SERVICES, INC.",
        "AT&T SERVICES INC",
        "AT&T SERVICES INC.",
    ],
    "CTIA - THE WIRELESS ASSOCIATION": [
        "CTIA - THE WIRELESS ASSOCIATION",
        "CTIA-THE WIRELESS ASSOCIATION",
    ],
    "NCTA - THE INTERNET & TELEVISION ASSOCIATION": [
        "NCTA - THE INTERNET & TELEVISION ASSOCIATION",
        "NCTA-THE INTERNET & TELEVISION ASSOCIATION",
    ],
    "TOYOTA MOTOR NORTH AMERICA": [
        "TOYOTA MOTOR NORTH AMERICA INC (TMA)",
        "TOYOTA MOTOR NORTH AMERICA, INC.",
    ],
    "VERIZON COMMUNICATIONS": [
        "VERIZON COMMUNICATIONS, INC.",
        "VERIZON COMMUNICATIONS",
        "VERIZON COMMUNICATIONS INC AND ITS SUBSIDIARIES",
        "VERIZON COMMUNICATIONS INC AND VARIOUS SUBSIDIARIES",
    ],
    "HP": ["HP INC", "HP INC."],
    "MEDTRONIC": ["MEDTRONIC INC", "MEDTRONIC, INC."],
    "LIBERTY MUTUAL GROUP": ["LIBERTY MUTUAL GROUP", "LIBERTY MUTUAL GROUP INC."],
    "CHARTER COMMUNICATIONS": [
        "CHARTER COMMUNICATIONS, INC.",
        "CHARTER COMMUNICATIONS INC.",
    ],
    "SPOTIFY": ["SPOTIFY", "SPOTIFY USA INC."],
    "INTERNATIONAL FRANCHISE ASSOCIATION": [
        "INTERNATIONAL FRANCHISE ASSOCIATION (IFA)",
        "INTERNATIONAL FRANCHISE ASSOCIATION",
    ],
    "AMERICAN FAMILY MUTUAL INSURANCE COMPANY": [
        "AMERICAN FAMILY MUTUAL INSURANCE COMPANY, S.I.",
        "AMERICAN FAMILY MUTUAL INSURANCE COMPANY",
    ],
    "LUMEN TECHNOLOGIES": [
        "LUMEN TECHNOLOGIES, INC.",
        "LUMEN TECHNOLOGIES, INC. (FORMERLY CENTURYLINK, INC.)",
    ],
    "PINTEREST": ["PINTEREST INC.", "PINTEREST, INC"],
    "ONFIDO": ["ONFIDO INC.", "ONFIDO, INC."],
    "UNIDOSUS": ["UNIDOSUS", "UNIDOSUS (FKA NATIONAL COUNCIL OF LA RAZA)"],
    "HOME DEPOT": ["THE HOME DEPOT", "HOME DEPOT"],
    "ROCKET LP": ["ROCKET LP", "ROCKET LP FKA RKT HOLDINGS"],
    "21ST CENTURY PRIVACY COALITION": [
        "21ST CENTURY PRIVACY COALITION",
        "FARRAGUT PARTNERS ON BEHALF OF 21ST CENTURY PRIVACY COALITION",
    ],
    "VISA": ["VISA, INC.", "VISA, U.S.A., INC."],
    "NEWS/MEDIA ALLIANCE": ["NEWS/MEDIA ALLIANCE", "NEWS MEDIA ALLIANCE"],
    "AIRBNB": ["AIRBNB", "AIRBNB, INC."],
    "PHARMACEUTICAL RESEARCH AND MANUFACTURERS OF AMERICA (PHRMA)": [
        "PHARMACEUTICAL RESEARCH AND MANUFACTURERS OF AMERICA (PHRMA)",
        "PHARMACEUTICAL RESEARCH AND MANUFACTURERS OF AMERICA",
    ],
    "TARGET CORPORATION": [
        "TARGET CORPORATION",
        "CORNERSTONE GOVERNMENT AFFAIRS OBO TARGET CORPORATION",
    ],
}
NAME_TO_GROUP = {name: g for g, names in NAME_GROUPS.items() for name in names}


def main() -> None:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = con.execute(QUERY).fetchall()
    con.close()

    merged: dict[str, dict] = {}
    for name, n_activities, n_filings, n_client_ids, first_year, last_year in rows:
        key = NAME_TO_GROUP.get(name, name)
        m = merged.setdefault(
            key,
            {"n_activities": 0, "n_filings": 0, "n_client_ids": 0,
             "first_year": 9999, "last_year": 0, "names": []},
        )
        m["n_activities"] += n_activities
        m["n_filings"] += n_filings
        m["n_client_ids"] += n_client_ids
        m["first_year"] = min(m["first_year"], first_year)
        m["last_year"] = max(m["last_year"], last_year)
        m["names"].append(name)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "entity", "n_activities", "n_filings", "n_client_ids",
            "first_year", "last_year", "n_years_span", "raw_names_merged",
        ])
        for k, m in sorted(merged.items(), key=lambda kv: -kv[1]["n_activities"]):
            w.writerow([
                k, m["n_activities"], m["n_filings"], m["n_client_ids"],
                m["first_year"], m["last_year"],
                m["last_year"] - m["first_year"] + 1,
                "; ".join(m["names"]),
            ])

    print(f"{len(rows)} raw name-rows -> {len(merged)} deduplicated entities")
    print(f"total activities: {sum(m['n_activities'] for m in merged.values())}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
