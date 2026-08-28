"""
Metadata, spatial centroids, aliases and neighbor graphs for all Ukrainian administrative regions.
"""
from typing import Dict, List, Any

# Region IDs and their properties
REGIONS: Dict[str, Dict[str, Any]] = {
    "UA-05": {
        "id": "UA-05",
        "name_ua": "Вінницька область",
        "name_ru": "Винницкая область",
        "name_en": "Vinnytsia Oblast",
        "short_ua": "Вінниччина",
        "aliases": ["вінниц", "винниц", "vinnytsia", "вінниччин", "ладинжин", "жмеринк"],
        "lat": 49.23, "lon": 28.46,
        "neighbors": ["UA-71", "UA-68", "UA-32", "UA-18", "UA-51", "UA-26"],
        "risk_weight": 0.65
    },
    "UA-07": {
        "id": "UA-07",
        "name_ua": "Волинська область",
        "name_ru": "Волынская область",
        "name_en": "Volyn Oblast",
        "short_ua": "Волинь",
        "aliases": ["волин", "волын", "volyn", "луцьк", "луцк", "ковель", "нововолинськ"],
        "lat": 51.21, "lon": 24.84,
        "neighbors": ["UA-56", "UA-46"],
        "risk_weight": 0.45
    },
    "UA-12": {
        "id": "UA-12",
        "name_ua": "Дніпропетровська область",
        "name_ru": "Днепропетровская область",
        "name_en": "Dnipropetrovsk Oblast",
        "short_ua": "Дніпропетровщина",
        "aliases": ["дніпро", "днепр", "днепропетровск", "кривий ріг", "кривой рог", "нікополь", "никополь", "павлоград", "кам'янське", "каменское"],
        "lat": 48.46, "lon": 35.04,
        "neighbors": ["UA-23", "UA-63", "UA-53", "UA-35", "UA-65", "UA-14"],
        "risk_weight": 0.92
    },
    "UA-14": {
        "id": "UA-14",
        "name_ua": "Донецька область",
        "name_ru": "Донецкая область",
        "name_en": "Donetsk Oblast",
        "short_ua": "Донеччина",
        "aliases": ["донецьк", "донецк", "краматорськ", "краматорск", "покровськ", "покровск", "слов'янськ", "славянск", "бахмут", "маріуполь", "мариуполь"],
        "lat": 48.00, "lon": 37.80,
        "neighbors": ["UA-44", "UA-63", "UA-12", "UA-23"],
        "risk_weight": 0.98
    },
    "UA-18": {
        "id": "UA-18",
        "name_ua": "Житомирська область",
        "name_ru": "Житомирская область",
        "name_en": "Zhytomyr Oblast",
        "short_ua": "Житомирщина",
        "aliases": ["житомир", "zhytomyr", "бердичів", "бердичев", "коростень", "новоград", "звягель"],
        "lat": 50.25, "lon": 28.66,
        "neighbors": ["UA-56", "UA-68", "UA-05", "UA-32"],
        "risk_weight": 0.60
    },
    "UA-21": {
        "id": "UA-21",
        "name_ua": "Закарпатська область",
        "name_ru": "Закарпатская область",
        "name_en": "Zakarpattia Oblast",
        "short_ua": "Закарпаття",
        "aliases": ["закарпат", "ужгород", "мукачев", "мукачево", "берегов", "хуст"],
        "lat": 48.62, "lon": 22.30,
        "neighbors": ["UA-46", "UA-26"],
        "risk_weight": 0.30
    },
    "UA-23": {
        "id": "UA-23",
        "name_ua": "Запорізька область",
        "name_ru": "Запорожская область",
        "name_en": "Zaporizhzhia Oblast",
        "short_ua": "Запоріжжя",
        "aliases": ["запоріж", "запорож", "zaporizhzhia", "мелітополь", "мелитополь", "бердянськ", "бердянск", "енергодар", "энергодар", "вільнянськ"],
        "lat": 47.83, "lon": 35.13,
        "neighbors": ["UA-12", "UA-14", "UA-65"],
        "risk_weight": 0.95
    },
    "UA-26": {
        "id": "UA-26",
        "name_ua": "Івано-Франківська область",
        "name_ru": "Ивано-Франковская область",
        "name_en": "Ivano-Frankivsk Oblast",
        "short_ua": "Прикарпаття",
        "aliases": ["івано-франківськ", "ивано-франковск", "франківськ", "прикарпаття", "калуш", "коломия", "бурштин"],
        "lat": 48.92, "lon": 24.71,
        "neighbors": ["UA-21", "UA-46", "UA-61", "UA-77", "UA-68"],
        "risk_weight": 0.50
    },
    "UA-30": {
        "id": "UA-30",
        "name_ua": "м. Київ",
        "name_ru": "г. Киев",
        "name_en": "Kyiv City",
        "short_ua": "Київ",
        "aliases": ["київ", "киев", "kyiv", "столиця", "столица", "бровари", "бориспіль", "боярка", "вишгород"],
        "lat": 50.45, "lon": 30.52,
        "neighbors": ["UA-32"],
        "risk_weight": 0.85
    },
    "UA-32": {
        "id": "UA-32",
        "name_ua": "Київська область",
        "name_ru": "Киевская область",
        "name_en": "Kyiv Oblast",
        "short_ua": "Київщина",
        "aliases": ["київськ", "киевск", "київщин", "біла церква", "белая церковь", "фастів", "фастов", "ірпінь", "ирпень", "буча", "гостомель", "васильків"],
        "lat": 50.15, "lon": 30.30,
        "neighbors": ["UA-30", "UA-74", "UA-71", "UA-18", "UA-05", "UA-53"],
        "risk_weight": 0.80
    },
    "UA-35": {
        "id": "UA-35",
        "name_ua": "Кіровоградська область",
        "name_ru": "Кировоградская область",
        "name_en": "Kirovohrad Oblast",
        "short_ua": "Кіровоградщина",
        "aliases": ["кіровоград", "кировоград", "кропивницьк", "кропивницк", "олександрія", "александрия", "знам'янка", "світловодськ"],
        "lat": 48.51, "lon": 32.26,
        "neighbors": ["UA-71", "UA-53", "UA-12", "UA-48", "UA-51", "UA-05"],
        "risk_weight": 0.70
    },
    "UA-44": {
        "id": "UA-44",
        "name_ua": "Луганська область",
        "name_ru": "Луганская область",
        "name_en": "Luhansk Oblast",
        "short_ua": "Луганщина",
        "aliases": ["луганськ", "луганск", "сєвєродонецьк", "северодонецк", "лисичанськ", "лисичанск", "алчевськ"],
        "lat": 48.57, "lon": 39.30,
        "neighbors": ["UA-63", "UA-14"],
        "risk_weight": 0.99
    },
    "UA-46": {
        "id": "UA-46",
        "name_ua": "Львівська область",
        "name_ru": "Львовская область",
        "name_en": "Lviv Oblast",
        "short_ua": "Львівщина",
        "aliases": ["львів", "львов", "lviv", "стрий", "дрогобич", "червоноград", "яворів", "броди", "самбір"],
        "lat": 49.83, "lon": 24.02,
        "neighbors": ["UA-07", "UA-56", "UA-61", "UA-26", "UA-21"],
        "risk_weight": 0.55
    },
    "UA-48": {
        "id": "UA-48",
        "name_ua": "Миколаївська область",
        "name_ru": "Николаевская область",
        "name_en": "Mykolaiv Oblast",
        "short_ua": "Миколаївщина",
        "aliases": ["миколаїв", "николаев", "mykolaiv", "очаків", "очаков", "вознесенськ", "первомайськ", "южноукраїнськ"],
        "lat": 46.97, "lon": 31.99,
        "neighbors": ["UA-51", "UA-35", "UA-12", "UA-65"],
        "risk_weight": 0.88
    },
    "UA-51": {
        "id": "UA-51",
        "name_ua": "Одеська область",
        "name_ru": "Одесская область",
        "name_en": "Odesa Oblast",
        "short_ua": "Одещина",
        "aliases": ["одес", "odesa", "odessa", "чорноморськ", "черноморск", "ізмаїл", "измаил", "білгород-дністровськ", "рені", "подільськ", "затока"],
        "lat": 46.48, "lon": 30.72,
        "neighbors": ["UA-48", "UA-35", "UA-05"],
        "risk_weight": 0.86
    },
    "UA-53": {
        "id": "UA-53",
        "name_ua": "Полтавська область",
        "name_ru": "Полтавская область",
        "name_en": "Poltava Oblast",
        "short_ua": "Полтавщина",
        "aliases": ["полтав", "кременчук", "кременчуг", "миргород", "лубни", "гадяч"],
        "lat": 49.58, "lon": 34.55,
        "neighbors": ["UA-59", "UA-63", "UA-12", "UA-35", "UA-71", "UA-32", "UA-74"],
        "risk_weight": 0.78
    },
    "UA-56": {
        "id": "UA-56",
        "name_ua": "Рівненська область",
        "name_ru": "Ровенская область",
        "name_en": "Rivne Oblast",
        "short_ua": "Рівненщина",
        "aliases": ["рівн", "ровн", "rivne", "дубно", "ваSequenceраш", "сарни", "острог", "костопіль"],
        "lat": 50.61, "lon": 26.25,
        "neighbors": ["UA-07", "UA-18", "UA-68", "UA-61", "UA-46"],
        "risk_weight": 0.50
    },
    "UA-59": {
        "id": "UA-59",
        "name_ua": "Сумська область",
        "name_ru": "Сумская область",
        "name_en": "Sumy Oblast",
        "short_ua": "Сумщина",
        "aliases": ["сум", "sumy", "конотоп", "шостк", "охтирк", "ахтырк", "ромен", "глухів", "глухов", "білопілл"],
        "lat": 50.90, "lon": 34.79,
        "neighbors": ["UA-74", "UA-53", "UA-63"],
        "risk_weight": 0.94
    },
    "UA-61": {
        "id": "UA-61",
        "name_ua": "Тернопільська область",
        "name_ru": "Тернопольская область",
        "name_en": "Ternopil Oblast",
        "short_ua": "Тернопільщина",
        "aliases": ["терноп", "ternopil", "чоplaceholderртків", "кременець", "бережани", "збараж"],
        "lat": 49.55, "lon": 25.59,
        "neighbors": ["UA-56", "UA-68", "UA-77", "UA-26", "UA-46"],
        "risk_weight": 0.52
    },
    "UA-63": {
        "id": "UA-63",
        "name_ua": "Харківська область",
        "name_ru": "Харьковская область",
        "name_en": "Kharkiv Oblast",
        "short_ua": "Харківщина",
        "aliases": ["харків", "харьков", "kharkiv", "ізюм", "изюм", "куп'янськ", "купянск", "чугуїв", "чугуев", "лозова", "люботин", "вовчанськ", "волчанск"],
        "lat": 49.99, "lon": 36.23,
        "neighbors": ["UA-59", "UA-44", "UA-14", "UA-12", "UA-53"],
        "risk_weight": 0.97
    },
    "UA-65": {
        "id": "UA-65",
        "name_ua": "Херсонська область",
        "name_ru": "Херсонская область",
        "name_en": "Kherson Oblast",
        "short_ua": "Херсонщина",
        "aliases": ["херсон", "kherson", "нова каховка", "берислав", "скадовськ", "генічеськ", "геническ", "чорнобаївк"],
        "lat": 46.63, "lon": 32.61,
        "neighbors": ["UA-48", "UA-12", "UA-23", "UA-43"],
        "risk_weight": 0.96
    },
    "UA-68": {
        "id": "UA-68",
        "name_ua": "Хмельницька область",
        "name_ru": "Хмельницкая область",
        "name_en": "Khmelnytskyi Oblast",
        "short_ua": "Хмельниччина",
        "aliases": ["хмельниц", "khmelnytskyi", "старокостянтинів", "староконстантинов", "кам'янець-подільськ", "шепетівк", "нетішин"],
        "lat": 49.42, "lon": 26.98,
        "neighbors": ["UA-56", "UA-18", "UA-05", "UA-77", "UA-61"],
        "risk_weight": 0.68  # Target airfield Starokostiantyniv
    },
    "UA-71": {
        "id": "UA-71",
        "name_ua": "Черкаська область",
        "name_ru": "Черкасская область",
        "name_en": "Cherkasy Oblast",
        "short_ua": "Черкащина",
        "aliases": ["черкас", "cherkasy", "умань", "сміла", "смела", "золотоноша", "канів", "канев"],
        "lat": 49.44, "lon": 32.06,
        "neighbors": ["UA-32", "UA-53", "UA-35", "UA-05"],
        "risk_weight": 0.72
    },
    "UA-74": {
        "id": "UA-74",
        "name_ua": "Чернігівська область",
        "name_ru": "Черниговская область",
        "name_en": "Chernihiv Oblast",
        "short_ua": "Чернігівщина",
        "aliases": ["чернігів", "чернигов", "chernihiv", "ніжин", "нежин", "прилуки", "прилуки", "новгород-сіверський"],
        "lat": 51.49, "lon": 31.28,
        "neighbors": ["UA-32", "UA-53", "UA-59"],
        "risk_weight": 0.85
    },
    "UA-77": {
        "id": "UA-77",
        "name_ua": "Чернівецька область",
        "name_ru": "Черновицкая область",
        "name_en": "Chernivtsi Oblast",
        "short_ua": "Буковина",
        "aliases": ["чернівц", "черновц", "буковин", "новоселиц", "сторожинец", "дністровськ"],
        "lat": 48.29, "lon": 25.93,
        "neighbors": ["UA-26", "UA-61", "UA-68"],
        "risk_weight": 0.40
    },
    "UA-43": {
        "id": "UA-43",
        "name_ua": "АР Крим",
        "name_ru": "АР Крым",
        "name_en": "Autonomous Republic of Crimea",
        "short_ua": "Крим",
        "aliases": ["крим", "крым", "севастополь", "сімферополь", "симферополь", "керч", "керчь", "джанкой", "євпаторія"],
        "lat": 44.95, "lon": 34.10,
        "neighbors": ["UA-65"],
        "risk_weight": 0.90
    }
}

# Lookup helpers
def find_regions_by_text(text: str) -> List[str]:
    """Identify which oblast IDs are mentioned in the given text."""
    text_lower = text.lower()
    matched = []
    
    # Check for "Вся Україна" / "All Ukraine" (e.g. MiG-31K takeoff)
    if any(k in text_lower for k in ["вся україна", "вся украина", "масштабна тривога", "по всій території", "по всей территории", "зліт міг", "взлет миг", "міг-31к", "миг-31к"]):
        return list(REGIONS.keys())

    for reg_id, data in REGIONS.items():
        if any(alias in text_lower for alias in data["aliases"]):
            matched.append(reg_id)
            
    return matched
