"""Generate a custom schema diagram grouped by namespace, excluding FTS/internal tables."""
import graphviz

COLORS = {
    'senate': '#dbeafe',   # blue
    'house':  '#dcfce7',   # green
    'press':  '#fef9c3',   # yellow
    'member': '#f3e8ff',   # purple
    'ref':    '#fee2e2',   # red
}

# Key columns to show per table (omit noisy address/contact fields)
TABLES = {
    # Senate
    'senate_filings':                    ['filing_uuid PK', 'registrant_id FK', 'client_id FK', 'filing_year', 'filing_period', 'income_amt', 'expenses_amt'],
    'senate_registrants':                ['id PK', 'name', 'house_registrant_id'],
    'senate_clients':                    ['id PK', 'name', 'state', 'country'],
    'senate_lobbyists':                  ['id PK', 'first_name', 'last_name'],
    'senate_lobbying_activities':        ['activity_id PK', 'filing_uuid FK', 'general_issue_code_display', 'description'],
    'senate_activity_lobbyists':         ['activity_id FK', 'lobbyist_id FK', 'covered_position'],
    'senate_activity_government_entities': ['activity_id FK', 'government_entity_id FK'],
    'senate_contribution_filings':       ['filing_uuid PK', 'registrant_id FK', 'lobbyist_id FK', 'filing_year'],
    'senate_contribution_items':         ['item_id PK', 'filing_uuid FK', 'honoree_name', 'amount_num', 'date'],
    'senate_contribution_pacs':          ['filing_uuid FK', 'pac_name'],
    'senate_filing_conviction_disclosures': ['filing_uuid FK', 'lobbyist_id FK', 'description'],
    'senate_filing_foreign_entities':    ['filing_uuid FK', 'name', 'country'],
    'senate_filing_affiliated_orgs':     ['filing_uuid FK', 'name'],
    # House
    'house_filings':                     ['house_filing_id PK', 'organization_name', 'client_name', 'senate_registrant_id FK', 'filing_year', 'income_amt'],
    'house_activities':                  ['activity_id PK', 'house_filing_id FK', 'issue_area_code', 'description'],
    'house_filing_lobbyists':            ['house_filing_id FK', 'first_name', 'last_name', 'covered_position'],
    'house_convictions':                 ['house_filing_id FK', 'lobbyist_name', 'description'],
    'house_foreign_entities':            ['house_filing_id FK', 'name', 'country'],
    'house_affiliated_orgs':             ['house_filing_id FK', 'name'],
    # Press
    'press_releases':                    ['release_id PK', 'url', 'date', 'bioguide_id FK', 'title', 'text'],
    'press_members':                     ['bioguide_id PK', 'name', 'party', 'state', 'chamber', 'n_releases'],
    # Member crosswalk
    'members':                           ['bioguide PK', 'official_full', 'last_party', 'last_state', 'is_current'],
    'member_terms':                      ['bioguide FK', 'type', 'state', 'party', 'start', 'end'],
    'member_committees':                 ['bioguide FK', 'committee_id FK', 'title', 'rank'],
    'committees':                        ['committee_id PK', 'name', 'type', 'parent_committee_id'],
    'honoree_member_map':                ['honoree_name PK', 'bioguide FK', 'method', 'confidence'],
    # Ref
    'ref_issue_codes':                   ['value PK', 'name'],
    'ref_government_entities':           ['id PK', 'name'],
    'ref_filing_types':                  ['value PK', 'name'],
    'ref_contribution_item_types':       ['value PK', 'name'],
}

NAMESPACE_ORDER = [
    ('senate', [t for t in TABLES if t.startswith('senate_')]),
    ('house',  [t for t in TABLES if t.startswith('house_')]),
    ('press',  [t for t in TABLES if t.startswith('press_')]),
    ('member', [t for t in TABLES if t.startswith('member') or t in ('members', 'committees', 'honoree_member_map')]),
    ('ref',    [t for t in TABLES if t.startswith('ref_')]),
]

EDGES = [
    # Senate internal
    ('senate_filings', 'senate_registrants', 'registrant_id'),
    ('senate_filings', 'senate_clients', 'client_id'),
    ('senate_lobbying_activities', 'senate_filings', 'filing_uuid'),
    ('senate_activity_lobbyists', 'senate_lobbying_activities', 'activity_id'),
    ('senate_activity_lobbyists', 'senate_lobbyists', 'lobbyist_id'),
    ('senate_activity_government_entities', 'senate_lobbying_activities', 'activity_id'),
    ('senate_activity_government_entities', 'ref_government_entities', 'government_entity_id'),
    ('senate_contribution_filings', 'senate_registrants', 'registrant_id'),
    ('senate_contribution_filings', 'senate_lobbyists', 'lobbyist_id'),
    ('senate_contribution_items', 'senate_contribution_filings', 'filing_uuid'),
    ('senate_contribution_pacs', 'senate_contribution_filings', 'filing_uuid'),
    ('senate_filing_conviction_disclosures', 'senate_filings', 'filing_uuid'),
    ('senate_filing_conviction_disclosures', 'senate_lobbyists', 'lobbyist_id'),
    ('senate_filing_foreign_entities', 'senate_filings', 'filing_uuid'),
    ('senate_filing_affiliated_orgs', 'senate_filings', 'filing_uuid'),
    # House internal
    ('house_activities', 'house_filings', 'house_filing_id'),
    ('house_filing_lobbyists', 'house_filings', 'house_filing_id'),
    ('house_convictions', 'house_filings', 'house_filing_id'),
    ('house_foreign_entities', 'house_filings', 'house_filing_id'),
    ('house_affiliated_orgs', 'house_filings', 'house_filing_id'),
    # Cross-chamber bridge
    ('house_filings', 'senate_registrants', 'senate_registrant_id'),
    # Press
    ('press_releases', 'members', 'bioguide_id'),
    # Member crosswalk
    ('member_terms', 'members', 'bioguide'),
    ('member_committees', 'members', 'bioguide'),
    ('member_committees', 'committees', 'committee_id'),
    ('honoree_member_map', 'members', 'bioguide'),
    # Say-vs-pay bridge
    ('senate_contribution_items', 'honoree_member_map', 'honoree_name'),
]

def table_label(name, cols):
    rows = ''.join(f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="9">{c}</FONT></TD></TR>' for c in cols)
    header = f'<TR><TD BGCOLOR="#555555"><FONT COLOR="white" POINT-SIZE="10"><B>{name}</B></FONT></TD></TR>'
    return f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">{header}{rows}</TABLE>>'

dot = graphviz.Digraph(
    'schema',
    graph_attr={
        'rankdir': 'LR',
        'splines': 'ortho',
        'nodesep': '0.4',
        'ranksep': '1.2',
        'fontname': 'Helvetica',
    },
    node_attr={'shape': 'plain', 'fontname': 'Helvetica'},
    edge_attr={'fontname': 'Helvetica', 'fontsize': '8', 'color': '#888888'},
)

for ns, tables in NAMESPACE_ORDER:
    with dot.subgraph(name=f'cluster_{ns}') as sg:
        sg.attr(label=ns.upper(), style='filled', fillcolor=COLORS[ns],
                color='#aaaaaa', fontsize='13', fontname='Helvetica Bold')
        for t in tables:
            sg.node(t, label=table_label(t, TABLES[t]))

for src, dst, label in EDGES:
    dot.edge(src, dst)

dot.render('schema_diagram', format='png', cleanup=True)
print("Saved schema_diagram.png")
