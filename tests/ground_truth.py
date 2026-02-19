"""Expected findings for the generated Czech legal test document."""

GROUND_TRUTH = {
    "whitespace": {
        "double_space": [
            {
                "paragraph_hint": "Celková cena díla",
                "section": "Článek 3 – Cena díla",
            },
            {
                "paragraph_hint": "Smlouva je vyhotovena ve",
                "section": "Článek 10 – Závěrečná ustanovení",
            },
            {
                "paragraph_hint": "Zhotovitel je povinen  informovat",
                "section": "Příloha č. 3 – Harmonogram prací",
            },
        ],
        "trailing_whitespace": [
            {
                "paragraph_hint": "V případě prodlení Zhotovitele s dokončením",
                "section": "Článek 4 – Termín plnění",
            }
        ],
        "leading_whitespace": [
            {
                "paragraph_hint": "Uplatněním smluvní pokuty",
                "section": "Článek 7 – Smluvní pokuty",
            }
        ],
        "consecutive_blank_paragraphs": [
            {"section": "Článek 6 – Předání a převzetí díla"}
        ],
    },
    "redundancy": {
        "verbatim": [
            {
                "section_a": "Článek 7 – Smluvní pokuty",
                "section_b": "Článek 9 – Odstoupení od smlouvy",
                "note": "Penalty clause verbatim duplicate",
            }
        ],
        "near_duplicate": [
            {
                "section_a": "Článek 2 – Předmět smlouvy",
                "section_b": "Článek 6 – Předání a převzetí díla",
                "note": "Scope paragraph nearly identical",
            },
            {
                "section_a": "5.1 Povinnosti Zhotovitele",
                "section_b": "Příloha č. 2 – Bezpečnostní předpisy",
                "note": "Duty paragraph near-duplicate",
            },
        ],
        "elaboration_not_redundant": [
            {
                "section_a": "Článek 2 – Předmět smlouvy",
                "section_b": "Příloha č. 1 – Projektová dokumentace",
                "note": "Příloha 1 elaborates Article 2 — should NOT be flagged as redundant",
            }
        ],
    },
    "references": {
        "valid_text_refs": [
            "čl. 4",
            "čl. 7",
            "článek 4",
            "článek 6",
            "článek 3",
            "příloha č. 1",
            "příloha č. 2",
            "§ 2586",
        ],
        "invalid_refs": [
            {
                "text": "článek 12",
                "section": "Článek 7 – Smluvní pokuty",
                "reason": "Article 12 does not exist",
            },
            {
                "text": "příloha č. 5",
                "section": "Článek 10 – Závěrečná ustanovení",
                "reason": "Příloha 5 does not exist",
            },
        ],
        "field_code_violations": "ALL references (none use Word field codes)",
    },
    "enumerations": {
        "good": ["2.1 Rozsah díla", "Příloha č. 2 – Bezpečnostní předpisy"],
        "bad": [
            {
                "section": "3.1 Platební podmínky",
                "issue": "mixed delimiters: comma/semicolon/comma/none",
            },
            {
                "section": "Článek 8 – Záruční podmínky",
                "issue": "inconsistent last items: semicolon/semicolon/comma/none",
            },
        ],
    },
}