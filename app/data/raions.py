"""
139 Raions of Ukraine mapped to Oblasts, Raion IDs and aliases for 100% district-level precision.
"""
from typing import Dict, List, Any, Optional
import re

ALL_RAIONS: Dict[str, Dict[str, Any]] = {
    "UA0102": {'id': 'UA0102', 'name_ua': 'Бахчисарайський', 'name_en': 'Bakhchysaraiskyi', 'oblast_id': 'UA-43', 'oblast_name_ua': 'Автономна Республіка Крим', 'aliases': ['бахчисарайський', 'бахчисарай']},
    "UA0104": {'id': 'UA0104', 'name_ua': 'Білогірський', 'name_en': 'Bilohirskyi', 'oblast_id': 'UA-43', 'oblast_name_ua': 'Автономна Республіка Крим', 'aliases': ['білогір', 'білогірський']},
    "UA0106": {'id': 'UA0106', 'name_ua': 'Джанкойський', 'name_en': 'Dzhankoiskyi', 'oblast_id': 'UA-43', 'oblast_name_ua': 'Автономна Республіка Крим', 'aliases': ['джанкойський', 'джанкой']},
    "UA0108": {'id': 'UA0108', 'name_ua': 'Євпаторійський', 'name_en': 'Yevpatoriiskyi', 'oblast_id': 'UA-43', 'oblast_name_ua': 'Автономна Республіка Крим', 'aliases': ['євпаторій', 'євпаторійський']},
    "UA0110": {'id': 'UA0110', 'name_ua': 'Керченський', 'name_en': 'Kerchenskyi', 'oblast_id': 'UA-43', 'oblast_name_ua': 'Автономна Республіка Крим', 'aliases': ['керченський', 'керчен']},
    "UA0112": {'id': 'UA0112', 'name_ua': 'Курманський', 'name_en': 'Kurmanskyi', 'oblast_id': 'UA-43', 'oblast_name_ua': 'Автономна Республіка Крим', 'aliases': ['курман', 'курманський']},
    "UA0114": {'id': 'UA0114', 'name_ua': 'Перекопський', 'name_en': 'Perekopskyi', 'oblast_id': 'UA-43', 'oblast_name_ua': 'Автономна Республіка Крим', 'aliases': ['перекоп', 'перекопський']},
    "UA0116": {'id': 'UA0116', 'name_ua': 'Сімферопольський', 'name_en': 'Simferopolskyi', 'oblast_id': 'UA-43', 'oblast_name_ua': 'Автономна Республіка Крим', 'aliases': ['сімферополь', 'сімферопольський']},
    "UA0118": {'id': 'UA0118', 'name_ua': 'Феодосійський', 'name_en': 'Feodosiiskyi', 'oblast_id': 'UA-43', 'oblast_name_ua': 'Автономна Республіка Крим', 'aliases': ['феодосійський', 'феодосій']},
    "UA0120": {'id': 'UA0120', 'name_ua': 'Ялтинський', 'name_en': 'Yaltynskyi', 'oblast_id': 'UA-43', 'oblast_name_ua': 'Автономна Республіка Крим', 'aliases': ['ялтинський', 'ялтин']},
    "UA0502": {'id': 'UA0502', 'name_ua': 'Вінницький', 'name_en': 'Vinnytskyi', 'oblast_id': 'UA-05', 'oblast_name_ua': 'Вінницька', 'aliases': ['вінни', 'вінницький']},
    "UA0504": {'id': 'UA0504', 'name_ua': 'Гайсинський', 'name_en': 'Haisynskyi', 'oblast_id': 'UA-05', 'oblast_name_ua': 'Вінницька', 'aliases': ['гайсинський', 'гайсин']},
    "UA0506": {'id': 'UA0506', 'name_ua': 'Жмеринський', 'name_en': 'Zhmerynskyi', 'oblast_id': 'UA-05', 'oblast_name_ua': 'Вінницька', 'aliases': ['жмерин', 'жмеринський']},
    "UA0508": {'id': 'UA0508', 'name_ua': 'Могилів-Подільський', 'name_en': 'Mohyliv-Podilskyi', 'oblast_id': 'UA-05', 'oblast_name_ua': 'Вінницька', 'aliases': ['могилів-подільський', 'могилів-поділь']},
    "UA0510": {'id': 'UA0510', 'name_ua': 'Тульчинський', 'name_en': 'Tulchynskyi', 'oblast_id': 'UA-05', 'oblast_name_ua': 'Вінницька', 'aliases': ['тульчин', 'тульчинський']},
    "UA0512": {'id': 'UA0512', 'name_ua': 'Хмільницький', 'name_en': 'Khmilnytskyi', 'oblast_id': 'UA-05', 'oblast_name_ua': 'Вінницька', 'aliases': ['хмільни', 'хмільницький']},
    "UA0702": {'id': 'UA0702', 'name_ua': 'Володимирський', 'name_en': 'Volodymyrskyi', 'oblast_id': 'UA-07', 'oblast_name_ua': 'Волинська', 'aliases': ['володимирський', 'володимир']},
    "UA0704": {'id': 'UA0704', 'name_ua': 'Камінь-Каширський', 'name_en': 'Kamin-Kashyrskyi', 'oblast_id': 'UA-07', 'oblast_name_ua': 'Волинська', 'aliases': ['камінь-кашир', 'камінь-каширський']},
    "UA0706": {'id': 'UA0706', 'name_ua': 'Ковельський', 'name_en': 'Kovelskyi', 'oblast_id': 'UA-07', 'oblast_name_ua': 'Волинська', 'aliases': ['ковельський', 'ковель']},
    "UA0708": {'id': 'UA0708', 'name_ua': 'Луцький', 'name_en': 'Lutskyi', 'oblast_id': 'UA-07', 'oblast_name_ua': 'Волинська', 'aliases': ['луцький', 'луцьк']},
    "UA1202": {'id': 'UA1202', 'name_ua': 'Дніпровський', 'name_en': 'Dniprovskyi', 'oblast_id': 'UA-12', 'oblast_name_ua': 'Дніпропетровська', 'aliases': ['дніпровський', 'дніпро']},
    "UA1204": {'id': 'UA1204', 'name_ua': "Кам'янський", 'name_en': 'Kamianskyi', 'oblast_id': 'UA-12', 'oblast_name_ua': 'Дніпропетровська', 'aliases': ["кам'янський", "кам'янське", "камянський", "камянське"]},
    "UA1206": {'id': 'UA1206', 'name_ua': 'Криворізький', 'name_en': 'Kryvorizkyi', 'oblast_id': 'UA-12', 'oblast_name_ua': 'Дніпропетровська', 'aliases': ['криворізький', 'кривий ріг', 'криворіжжя']},
    "UA1208": {'id': 'UA1208', 'name_ua': 'Нікопольський', 'name_en': 'Nikopolskyi', 'oblast_id': 'UA-12', 'oblast_name_ua': 'Дніпропетровська', 'aliases': ['нікопольський', 'нікополь']},
    "UA1210": {'id': 'UA1210', 'name_ua': 'Самарівський', 'name_en': 'Samarivskyi', 'oblast_id': 'UA-12', 'oblast_name_ua': 'Дніпропетровська', 'aliases': ['самарівський', 'самарів', 'новомосковський', 'новомосковськ']},
    "UA1212": {'id': 'UA1212', 'name_ua': 'Павлоградський', 'name_en': 'Pavlohradskyi', 'oblast_id': 'UA-12', 'oblast_name_ua': 'Дніпропетровська', 'aliases': ['павлоградський', 'павлоград']},
    "UA1214": {'id': 'UA1214', 'name_ua': 'Синельниківський', 'name_en': 'Synelnykivskyi', 'oblast_id': 'UA-12', 'oblast_name_ua': 'Дніпропетровська', 'aliases': ['синельниківський', 'синельникове']},
    "UA1402": {'id': 'UA1402', 'name_ua': 'Бахмутський', 'name_en': 'Bakhmutskyi', 'oblast_id': 'UA-14', 'oblast_name_ua': 'Донецька', 'aliases': ['бахмутський', 'бахмут']},
    "UA1404": {'id': 'UA1404', 'name_ua': 'Волноваський', 'name_en': 'Volnovaskyi', 'oblast_id': 'UA-14', 'oblast_name_ua': 'Донецька', 'aliases': ['волноваський', 'волноваха']},
    "UA1406": {'id': 'UA1406', 'name_ua': 'Горлівський', 'name_en': 'Horlivskyi', 'oblast_id': 'UA-14', 'oblast_name_ua': 'Донецька', 'aliases': ['горлівський', 'горлівка']},
    "UA1408": {'id': 'UA1408', 'name_ua': 'Донецький', 'name_en': 'Donetskyi', 'oblast_id': 'UA-14', 'oblast_name_ua': 'Донецька', 'aliases': ['донецький', 'донецьк']},
    "UA1410": {'id': 'UA1410', 'name_ua': 'Кальміуський', 'name_en': 'Kalmiuskyi', 'oblast_id': 'UA-14', 'oblast_name_ua': 'Донецька', 'aliases': ['кальміуський', 'кальміу']},
    "UA1412": {'id': 'UA1412', 'name_ua': 'Краматорський', 'name_en': 'Kramatorskyi', 'oblast_id': 'UA-14', 'oblast_name_ua': 'Донецька', 'aliases': ['краматор', 'краматорський']},
    "UA1414": {'id': 'UA1414', 'name_ua': 'Маріупольський', 'name_en': 'Mariupolskyi', 'oblast_id': 'UA-14', 'oblast_name_ua': 'Донецька', 'aliases': ['маріупольський', 'маріуполь']},
    "UA1416": {'id': 'UA1416', 'name_ua': 'Покровський', 'name_en': 'Pokrovskyi', 'oblast_id': 'UA-14', 'oblast_name_ua': 'Донецька', 'aliases': ['покровський', 'покров']},
    "UA1802": {'id': 'UA1802', 'name_ua': 'Бердичівський', 'name_en': 'Berdychivskyi', 'oblast_id': 'UA-18', 'oblast_name_ua': 'Житомирська', 'aliases': ['бердичівський', 'бердичів']},
    "UA1804": {'id': 'UA1804', 'name_ua': 'Житомирський', 'name_en': 'Zhytomyrskyi', 'oblast_id': 'UA-18', 'oblast_name_ua': 'Житомирська', 'aliases': ['житомирський', 'житомир']},
    "UA1806": {'id': 'UA1806', 'name_ua': 'Коростенський', 'name_en': 'Korostenskyi', 'oblast_id': 'UA-18', 'oblast_name_ua': 'Житомирська', 'aliases': ['коростен', 'коростенський']},
    "UA1808": {'id': 'UA1808', 'name_ua': 'Звягельський', 'name_en': 'Zviahelskyi', 'oblast_id': 'UA-18', 'oblast_name_ua': 'Житомирська', 'aliases': ['звягельський', 'звягель']},
    "UA2102": {'id': 'UA2102', 'name_ua': 'Берегівський', 'name_en': 'Berehivskyi', 'oblast_id': 'UA-21', 'oblast_name_ua': 'Закарпатська', 'aliases': ['берегівський', 'берегів']},
    "UA2104": {'id': 'UA2104', 'name_ua': 'Мукачівський', 'name_en': 'Mukachivskyi', 'oblast_id': 'UA-21', 'oblast_name_ua': 'Закарпатська', 'aliases': ['мукачівський', 'мукачів']},
    "UA2106": {'id': 'UA2106', 'name_ua': 'Рахівський', 'name_en': 'Rakhivskyi', 'oblast_id': 'UA-21', 'oblast_name_ua': 'Закарпатська', 'aliases': ['рахів', 'рахівський']},
    "UA2108": {'id': 'UA2108', 'name_ua': 'Тячівський', 'name_en': 'Tiachivskyi', 'oblast_id': 'UA-21', 'oblast_name_ua': 'Закарпатська', 'aliases': ['тячівський', 'тячів']},
    "UA2110": {'id': 'UA2110', 'name_ua': 'Ужгородський', 'name_en': 'Uzhhorodskyi', 'oblast_id': 'UA-21', 'oblast_name_ua': 'Закарпатська', 'aliases': ['ужгород', 'ужгородський']},
    "UA2112": {'id': 'UA2112', 'name_ua': 'Хустський', 'name_en': 'Khustskyi', 'oblast_id': 'UA-21', 'oblast_name_ua': 'Закарпатська', 'aliases': ['хустський', 'хуст']},
    "UA2302": {'id': 'UA2302', 'name_ua': 'Бердянський', 'name_en': 'Berdianskyi', 'oblast_id': 'UA-23', 'oblast_name_ua': 'Запорізька', 'aliases': ['бердянський', 'бердян']},
    "UA2304": {'id': 'UA2304', 'name_ua': 'Василівський', 'name_en': 'Vasylivskyi', 'oblast_id': 'UA-23', 'oblast_name_ua': 'Запорізька', 'aliases': ['василів', 'василівський']},
    "UA2306": {'id': 'UA2306', 'name_ua': 'Запорізький', 'name_en': 'Zaporizkyi', 'oblast_id': 'UA-23', 'oblast_name_ua': 'Запорізька', 'aliases': ['запорізький', 'запорі']},
    "UA2308": {'id': 'UA2308', 'name_ua': 'Мелітопольський', 'name_en': 'Melitopolskyi', 'oblast_id': 'UA-23', 'oblast_name_ua': 'Запорізька', 'aliases': ['мелітопольський', 'мелітополь']},
    "UA2310": {'id': 'UA2310', 'name_ua': 'Пологівський', 'name_en': 'Polohivskyi', 'oblast_id': 'UA-23', 'oblast_name_ua': 'Запорізька', 'aliases': ['пологівський', 'пологів']},
    "UA2602": {'id': 'UA2602', 'name_ua': 'Верховинський', 'name_en': 'Verkhovynskyi', 'oblast_id': 'UA-26', 'oblast_name_ua': 'Івано-Франківська', 'aliases': ['верховинський', 'верховин']},
    "UA2604": {'id': 'UA2604', 'name_ua': 'Івано-Франківський', 'name_en': 'Ivano-Frankivskyi', 'oblast_id': 'UA-26', 'oblast_name_ua': 'Івано-Франківська', 'aliases': ['івано-франків', 'івано-франківський']},
    "UA2606": {'id': 'UA2606', 'name_ua': 'Калуський', 'name_en': 'Kaluskyi', 'oblast_id': 'UA-26', 'oblast_name_ua': 'Івано-Франківська', 'aliases': ['калуський', 'калу']},
    "UA2608": {'id': 'UA2608', 'name_ua': 'Коломийський', 'name_en': 'Kolomyiskyi', 'oblast_id': 'UA-26', 'oblast_name_ua': 'Івано-Франківська', 'aliases': ['коломийський', 'коломий']},
    "UA2610": {'id': 'UA2610', 'name_ua': 'Косівський', 'name_en': 'Kosivskyi', 'oblast_id': 'UA-26', 'oblast_name_ua': 'Івано-Франківська', 'aliases': ['косів', 'косівський']},
    "UA2612": {'id': 'UA2612', 'name_ua': 'Надвірнянський', 'name_en': 'Nadvirnianskyi', 'oblast_id': 'UA-26', 'oblast_name_ua': 'Івано-Франківська', 'aliases': ['надвірнян', 'надвірнянський']},
    "UA3200": {'id': 'UA3200', 'name_ua': 'Чорнобильська зона відчуження', 'name_en': 'Chornobyl Exclusion Zone', 'oblast_id': 'UA-32', 'oblast_name_ua': 'Київська', 'aliases': ['чорнобильська зона відчуження', 'чорнобиль', 'зона відчуження', 'чорнобильськ']},
    "UA3202": {'id': 'UA3202', 'name_ua': 'Білоцерківський', 'name_en': 'Bilotserkivskyi', 'oblast_id': 'UA-32', 'oblast_name_ua': 'Київська', 'aliases': ['білоцерків', 'білоцерківський']},
    "UA3204": {'id': 'UA3204', 'name_ua': 'Бориспільський', 'name_en': 'Boryspilskyi', 'oblast_id': 'UA-32', 'oblast_name_ua': 'Київська', 'aliases': ['бориспільський', 'бориспіль']},
    "UA3206": {'id': 'UA3206', 'name_ua': 'Броварський', 'name_en': 'Brovarskyi', 'oblast_id': 'UA-32', 'oblast_name_ua': 'Київська', 'aliases': ['бровар', 'броварський']},
    "UA3208": {'id': 'UA3208', 'name_ua': 'Бучанський', 'name_en': 'Buchanskyi', 'oblast_id': 'UA-32', 'oblast_name_ua': 'Київська', 'aliases': ['бучан', 'бучанський']},
    "UA3210": {'id': 'UA3210', 'name_ua': 'Вишгородський', 'name_en': 'Vyshhorodskyi', 'oblast_id': 'UA-32', 'oblast_name_ua': 'Київська', 'aliases': ['вишгород', 'вишгородський']},
    "UA3212": {'id': 'UA3212', 'name_ua': 'Обухівський', 'name_en': 'Obukhivskyi', 'oblast_id': 'UA-32', 'oblast_name_ua': 'Київська', 'aliases': ['обухівський', 'обухів']},
    "UA3214": {'id': 'UA3214', 'name_ua': 'Фастівський', 'name_en': 'Fastivskyi', 'oblast_id': 'UA-32', 'oblast_name_ua': 'Київська', 'aliases': ['фастівський', 'фастів']},
    "UA3502": {'id': 'UA3502', 'name_ua': 'Голованівський', 'name_en': 'Holovanivskyi', 'oblast_id': 'UA-35', 'oblast_name_ua': 'Кіровоградська', 'aliases': ['голованів', 'голованівський']},
    "UA3504": {'id': 'UA3504', 'name_ua': 'Кропивницький', 'name_en': 'Kropyvnytskyi', 'oblast_id': 'UA-35', 'oblast_name_ua': 'Кіровоградська', 'aliases': ['кропивницький', 'кропивни']},
    "UA3506": {'id': 'UA3506', 'name_ua': 'Новоукраїнський', 'name_en': 'Novoukrainskyi', 'oblast_id': 'UA-35', 'oblast_name_ua': 'Кіровоградська', 'aliases': ['новоукраїнський', 'новоукраїн']},
    "UA3508": {'id': 'UA3508', 'name_ua': 'Олександрійський', 'name_en': 'Oleksandriiskyi', 'oblast_id': 'UA-35', 'oblast_name_ua': 'Кіровоградська', 'aliases': ['олександрій', 'олександрійський']},
    "UA4402": {'id': 'UA4402', 'name_ua': 'Алчевський', 'name_en': 'Alchevskyi', 'oblast_id': 'UA-44', 'oblast_name_ua': 'Луганська', 'aliases': ['алчевський', 'алчев']},
    "UA4404": {'id': 'UA4404', 'name_ua': 'Довжанський', 'name_en': 'Dovzhanskyi', 'oblast_id': 'UA-44', 'oblast_name_ua': 'Луганська', 'aliases': ['довжанський', 'довжан']},
    "UA4406": {'id': 'UA4406', 'name_ua': 'Луганський', 'name_en': 'Luhanskyi', 'oblast_id': 'UA-44', 'oblast_name_ua': 'Луганська', 'aliases': ['луган', 'луганський']},
    "UA4408": {'id': 'UA4408', 'name_ua': 'Ровеньківський', 'name_en': 'Rovenkivskyi', 'oblast_id': 'UA-44', 'oblast_name_ua': 'Луганська', 'aliases': ['ровеньків', 'ровеньківський']},
    "UA4410": {'id': 'UA4410', 'name_ua': 'Сватівський', 'name_en': 'Svativskyi', 'oblast_id': 'UA-44', 'oblast_name_ua': 'Луганська', 'aliases': ['сватів', 'сватівський']},
    "UA4412": {'id': 'UA4412', 'name_ua': 'Сіверськодонецький', 'name_en': 'Siverskodonetskyi', 'oblast_id': 'UA-44', 'oblast_name_ua': 'Луганська', 'aliases': ['сіверськодонецький', 'сіверськодоне']},
    "UA4414": {'id': 'UA4414', 'name_ua': 'Старобільський', 'name_en': 'Starobilskyi', 'oblast_id': 'UA-44', 'oblast_name_ua': 'Луганська', 'aliases': ['старобільський', 'старобіль']},
    "UA4416": {'id': 'UA4416', 'name_ua': 'Щастинський', 'name_en': 'Shchastynskyi', 'oblast_id': 'UA-44', 'oblast_name_ua': 'Луганська', 'aliases': ['щастин', 'щастинський']},
    "UA4602": {'id': 'UA4602', 'name_ua': 'Дрогобицький', 'name_en': 'Drohobytskyi', 'oblast_id': 'UA-46', 'oblast_name_ua': 'Львівська', 'aliases': ['дрогобицький', 'дрогоби']},
    "UA4604": {'id': 'UA4604', 'name_ua': 'Золочівський', 'name_en': 'Zolochivskyi', 'oblast_id': 'UA-46', 'oblast_name_ua': 'Львівська', 'aliases': ['золочівський', 'золочів']},
    "UA4606": {'id': 'UA4606', 'name_ua': 'Львівський', 'name_en': 'Lvivskyi', 'oblast_id': 'UA-46', 'oblast_name_ua': 'Львівська', 'aliases': ['львівський', 'львів']},
    "UA4608": {'id': 'UA4608', 'name_ua': 'Самбірський', 'name_en': 'Sambirskyi', 'oblast_id': 'UA-46', 'oblast_name_ua': 'Львівська', 'aliases': ['самбірський', 'самбір']},
    "UA4610": {'id': 'UA4610', 'name_ua': 'Стрийський', 'name_en': 'Stryiskyi', 'oblast_id': 'UA-46', 'oblast_name_ua': 'Львівська', 'aliases': ['стрийський', 'стрий']},
    "UA4612": {'id': 'UA4612', 'name_ua': 'Шептицький', 'name_en': 'Sheptytskyi', 'oblast_id': 'UA-46', 'oblast_name_ua': 'Львівська', 'aliases': ['шептицький', 'шепти']},
    "UA4614": {'id': 'UA4614', 'name_ua': 'Яворівський', 'name_en': 'Yavorivskyi', 'oblast_id': 'UA-46', 'oblast_name_ua': 'Львівська', 'aliases': ['яворівський', 'яворів']},
    "UA4802": {'id': 'UA4802', 'name_ua': 'Баштанський', 'name_en': 'Bashtanskyi', 'oblast_id': 'UA-48', 'oblast_name_ua': 'Миколаївська', 'aliases': ['баштан', 'баштанський']},
    "UA4804": {'id': 'UA4804', 'name_ua': 'Вознесенський', 'name_en': 'Voznesenskyi', 'oblast_id': 'UA-48', 'oblast_name_ua': 'Миколаївська', 'aliases': ['вознесен', 'вознесенський']},
    "UA4806": {'id': 'UA4806', 'name_ua': 'Миколаївський', 'name_en': 'Mykolaivskyi', 'oblast_id': 'UA-48', 'oblast_name_ua': 'Миколаївська', 'aliases': ['миколаїв', 'миколаївський']},
    "UA4808": {'id': 'UA4808', 'name_ua': 'Первомайський', 'name_en': 'Pervomaiskyi', 'oblast_id': 'UA-48', 'oblast_name_ua': 'Миколаївська', 'aliases': ['первомайський', 'первомай']},
    "UA5102": {'id': 'UA5102', 'name_ua': 'Березівський', 'name_en': 'Berezivskyi', 'oblast_id': 'UA-51', 'oblast_name_ua': 'Одеська', 'aliases': ['березів', 'березівський']},
    "UA5104": {'id': 'UA5104', 'name_ua': 'Білгород-Дністровський', 'name_en': 'Bilhorod-Dnistrovskyi', 'oblast_id': 'UA-51', 'oblast_name_ua': 'Одеська', 'aliases': ['білгород-дністровський', 'білгород-дністров']},
    "UA5106": {'id': 'UA5106', 'name_ua': 'Болградський', 'name_en': 'Bolhradskyi', 'oblast_id': 'UA-51', 'oblast_name_ua': 'Одеська', 'aliases': ['болградський', 'болград']},
    "UA5108": {'id': 'UA5108', 'name_ua': 'Ізмаїльський', 'name_en': 'Izmailskyi', 'oblast_id': 'UA-51', 'oblast_name_ua': 'Одеська', 'aliases': ['ізмаїльський', 'ізмаїль']},
    "UA5110": {'id': 'UA5110', 'name_ua': 'Одеський', 'name_en': 'Odeskyi', 'oblast_id': 'UA-51', 'oblast_name_ua': 'Одеська', 'aliases': ['одеський', 'оде']},
    "UA5112": {'id': 'UA5112', 'name_ua': 'Подільський', 'name_en': 'Podilskyi', 'oblast_id': 'UA-51', 'oblast_name_ua': 'Одеська', 'aliases': ['поділь', 'подільський']},
    "UA5114": {'id': 'UA5114', 'name_ua': 'Роздільнянський', 'name_en': 'Rozdilnianskyi', 'oblast_id': 'UA-51', 'oblast_name_ua': 'Одеська', 'aliases': ['роздільнянський', 'роздільнян']},
    "UA5302": {'id': 'UA5302', 'name_ua': 'Кременчуцький', 'name_en': 'Kremenchutskyi', 'oblast_id': 'UA-53', 'oblast_name_ua': 'Полтавська', 'aliases': ['кременчу', 'кременчуцький']},
    "UA5304": {'id': 'UA5304', 'name_ua': 'Лубенський', 'name_en': 'Lubenskyi', 'oblast_id': 'UA-53', 'oblast_name_ua': 'Полтавська', 'aliases': ['лубен', 'лубенський']},
    "UA5306": {'id': 'UA5306', 'name_ua': 'Миргородський', 'name_en': 'Myrhorodskyi', 'oblast_id': 'UA-53', 'oblast_name_ua': 'Полтавська', 'aliases': ['миргородський', 'миргород']},
    "UA5308": {'id': 'UA5308', 'name_ua': 'Полтавський', 'name_en': 'Poltavskyi', 'oblast_id': 'UA-53', 'oblast_name_ua': 'Полтавська', 'aliases': ['полтавський', 'полтав']},
    "UA5602": {'id': 'UA5602', 'name_ua': 'Вараський', 'name_en': 'Varaskyi', 'oblast_id': 'UA-56', 'oblast_name_ua': 'Рівненська', 'aliases': ['вараський', 'вара']},
    "UA5604": {'id': 'UA5604', 'name_ua': 'Дубенський', 'name_en': 'Dubenskyi', 'oblast_id': 'UA-56', 'oblast_name_ua': 'Рівненська', 'aliases': ['дубен', 'дубенський']},
    "UA5606": {'id': 'UA5606', 'name_ua': 'Рівненський', 'name_en': 'Rivnenskyi', 'oblast_id': 'UA-56', 'oblast_name_ua': 'Рівненська', 'aliases': ['рівнен', 'рівненський']},
    "UA5608": {'id': 'UA5608', 'name_ua': 'Сарненський', 'name_en': 'Sarnenskyi', 'oblast_id': 'UA-56', 'oblast_name_ua': 'Рівненська', 'aliases': ['сарненський', 'сарнен']},
    "UA5902": {'id': 'UA5902', 'name_ua': 'Конотопський', 'name_en': 'Konotopskyi', 'oblast_id': 'UA-59', 'oblast_name_ua': 'Сумська', 'aliases': ['конотопський', 'конотоп']},
    "UA5904": {'id': 'UA5904', 'name_ua': 'Охтирський', 'name_en': 'Okhtyrskyi', 'oblast_id': 'UA-59', 'oblast_name_ua': 'Сумська', 'aliases': ['охтир', 'охтирський']},
    "UA5906": {'id': 'UA5906', 'name_ua': 'Роменський', 'name_en': 'Romenskyi', 'oblast_id': 'UA-59', 'oblast_name_ua': 'Сумська', 'aliases': ['роменський', 'ромен']},
    "UA5908": {'id': 'UA5908', 'name_ua': 'Сумський', 'name_en': 'Sumskyi', 'oblast_id': 'UA-59', 'oblast_name_ua': 'Сумська', 'aliases': ['сумський', 'сум']},
    "UA5910": {'id': 'UA5910', 'name_ua': 'Шосткинський', 'name_en': 'Shostkynskyi', 'oblast_id': 'UA-59', 'oblast_name_ua': 'Сумська', 'aliases': ['шосткин', 'шосткинський']},
    "UA6102": {'id': 'UA6102', 'name_ua': 'Кременецький', 'name_en': 'Kremenetskyi', 'oblast_id': 'UA-61', 'oblast_name_ua': 'Тернопільська', 'aliases': ['кременецький', 'кремене']},
    "UA6104": {'id': 'UA6104', 'name_ua': 'Тернопільський', 'name_en': 'Ternopilskyi', 'oblast_id': 'UA-61', 'oblast_name_ua': 'Тернопільська', 'aliases': ['тернопільський', 'тернопіль']},
    "UA6106": {'id': 'UA6106', 'name_ua': 'Чортківський', 'name_en': 'Chortkivskyi', 'oblast_id': 'UA-61', 'oblast_name_ua': 'Тернопільська', 'aliases': ['чортків', 'чортківський']},
    "UA6302": {'id': 'UA6302', 'name_ua': 'Богодухівський', 'name_en': 'Bohodukhivskyi', 'oblast_id': 'UA-63', 'oblast_name_ua': 'Харківська', 'aliases': ['богодухів', 'богодухівський']},
    "UA6304": {'id': 'UA6304', 'name_ua': 'Ізюмський', 'name_en': 'Iziumskyi', 'oblast_id': 'UA-63', 'oblast_name_ua': 'Харківська', 'aliases': ['ізюмський', 'ізюм']},
    "UA6306": {'id': 'UA6306', 'name_ua': 'Берестинський', 'name_en': 'Berestynskyi', 'oblast_id': 'UA-63', 'oblast_name_ua': 'Харківська', 'aliases': ['берестин', 'берестинський']},
    "UA6308": {'id': 'UA6308', 'name_ua': "Куп'янський", 'name_en': 'Kupianskyi', 'oblast_id': 'UA-63', 'oblast_name_ua': 'Харківська', 'aliases': ["куп'янський", "куп'ян"]},
    "UA6310": {'id': 'UA6310', 'name_ua': 'Лозівський', 'name_en': 'Lozivskyi', 'oblast_id': 'UA-63', 'oblast_name_ua': 'Харківська', 'aliases': ['лозівський', 'лозів']},
    "UA6312": {'id': 'UA6312', 'name_ua': 'Харківський', 'name_en': 'Kharkivskyi', 'oblast_id': 'UA-63', 'oblast_name_ua': 'Харківська', 'aliases': ['харків', 'харківський']},
    "UA6314": {'id': 'UA6314', 'name_ua': 'Чугуївський', 'name_en': 'Chuhuivskyi', 'oblast_id': 'UA-63', 'oblast_name_ua': 'Харківська', 'aliases': ['чугуїв', 'чугуївський']},
    "UA6502": {'id': 'UA6502', 'name_ua': 'Бериславський', 'name_en': 'Beryslavskyi', 'oblast_id': 'UA-65', 'oblast_name_ua': 'Херсонська', 'aliases': ['берислав', 'бериславський']},
    "UA6504": {'id': 'UA6504', 'name_ua': 'Генічеський', 'name_en': 'Henicheskyi', 'oblast_id': 'UA-65', 'oblast_name_ua': 'Херсонська', 'aliases': ['геніче', 'генічеський']},
    "UA6506": {'id': 'UA6506', 'name_ua': 'Каховський', 'name_en': 'Kakhovskyi', 'oblast_id': 'UA-65', 'oblast_name_ua': 'Херсонська', 'aliases': ['каховський', 'кахов']},
    "UA6508": {'id': 'UA6508', 'name_ua': 'Скадовський', 'name_en': 'Skadovskyi', 'oblast_id': 'UA-65', 'oblast_name_ua': 'Херсонська', 'aliases': ['скадов', 'скадовський']},
    "UA6510": {'id': 'UA6510', 'name_ua': 'Херсонський', 'name_en': 'Khersonskyi', 'oblast_id': 'UA-65', 'oblast_name_ua': 'Херсонська', 'aliases': ['херсон', 'херсонський']},
    "UA6802": {'id': 'UA6802', 'name_ua': "Кам'янець-Подільський", 'name_en': 'Kamianets-Podilskyi', 'oblast_id': 'UA-68', 'oblast_name_ua': 'Хмельницька', 'aliases': ["кам'янець-подільський", "кам'янець-поділь"]},
    "UA6804": {'id': 'UA6804', 'name_ua': 'Хмельницький', 'name_en': 'Khmelnytskyi', 'oblast_id': 'UA-68', 'oblast_name_ua': 'Хмельницька', 'aliases': ['хмельницький', 'хмельни']},
    "UA6806": {'id': 'UA6806', 'name_ua': 'Шепетівський', 'name_en': 'Shepetivskyi', 'oblast_id': 'UA-68', 'oblast_name_ua': 'Хмельницька', 'aliases': ['шепетівський', 'шепетів']},
    "UA7102": {'id': 'UA7102', 'name_ua': 'Звенигородський', 'name_en': 'Zvenyhorodskyi', 'oblast_id': 'UA-71', 'oblast_name_ua': 'Черкаська', 'aliases': ['звенигородський', 'звенигород']},
    "UA7104": {'id': 'UA7104', 'name_ua': 'Золотоніський', 'name_en': 'Zolotoniskyi', 'oblast_id': 'UA-71', 'oblast_name_ua': 'Черкаська', 'aliases': ['золотоні', 'золотоніський']},
    "UA7106": {'id': 'UA7106', 'name_ua': 'Уманський', 'name_en': 'Umanskyi', 'oblast_id': 'UA-71', 'oblast_name_ua': 'Черкаська', 'aliases': ['уман', 'уманський']},
    "UA7108": {'id': 'UA7108', 'name_ua': 'Черкаський', 'name_en': 'Cherkaskyi', 'oblast_id': 'UA-71', 'oblast_name_ua': 'Черкаська', 'aliases': ['черкаський', 'черка']},
    "UA7302": {'id': 'UA7302', 'name_ua': 'Вижницький', 'name_en': 'Vyzhnytskyi', 'oblast_id': 'UA-77', 'oblast_name_ua': 'Чернівецька', 'aliases': ['вижницький', 'вижни']},
    "UA7304": {'id': 'UA7304', 'name_ua': 'Дністровський', 'name_en': 'Dnistrovskyi', 'oblast_id': 'UA-77', 'oblast_name_ua': 'Чернівецька', 'aliases': ['дністровський', 'дністров']},
    "UA7306": {'id': 'UA7306', 'name_ua': 'Чернівецький', 'name_en': 'Chernivetskyi', 'oblast_id': 'UA-77', 'oblast_name_ua': 'Чернівецька', 'aliases': ['черніве', 'чернівецький']},
    "UA7402": {'id': 'UA7402', 'name_ua': 'Корюківський', 'name_en': 'Koriukivskyi', 'oblast_id': 'UA-74', 'oblast_name_ua': 'Чернігівська', 'aliases': ['корюків', 'корюківський']},
    "UA7404": {'id': 'UA7404', 'name_ua': 'Ніжинський', 'name_en': 'Nizhynskyi', 'oblast_id': 'UA-74', 'oblast_name_ua': 'Чернігівська', 'aliases': ['ніжинський', 'ніжин']},
    "UA7406": {'id': 'UA7406', 'name_ua': 'Новгород-Сіверський', 'name_en': 'Novhorod-Siverskyi', 'oblast_id': 'UA-74', 'oblast_name_ua': 'Чернігівська', 'aliases': ['новгород-сівер', 'новгород-сіверський']},
    "UA7408": {'id': 'UA7408', 'name_ua': 'Прилуцький', 'name_en': 'Prylutskyi', 'oblast_id': 'UA-74', 'oblast_name_ua': 'Чернігівська', 'aliases': ['прилуцький', 'прилуки', 'прилук']},
    "UA7410": {'id': 'UA7410', 'name_ua': 'Чернігівський', 'name_en': 'Chernihivskyi', 'oblast_id': 'UA-74', 'oblast_name_ua': 'Чернігівська', 'aliases': ['чернігівський', 'чернігів']},
    "UA8000": {'id': 'UA8000', 'name_ua': 'Київ', 'name_en': 'Kyiv', 'oblast_id': 'UA-30', 'oblast_name_ua': 'Київ', 'aliases': ['київ']},
    "UA8500": {'id': 'UA8500', 'name_ua': 'Севастополь', 'name_en': 'Sevastopol', 'oblast_id': 'UA-40', 'oblast_name_ua': 'Севастополь', 'aliases': ['севастополь']},
}

def normalize_ukrainian_text(text: str) -> str:
    t = text.lower().replace('_', ' ').replace('-', ' ')
    for c in ['’', '‘', 'ʼ', '`', '\'', '"']:
        t = t.replace(c, "'")
    return t

def find_raions_in_text(text: str) -> List[Dict[str, Any]]:
    """Finds all matching districts/raions mentioned in text or hashtags using Cyrillic boundaries."""
    t_norm = normalize_ukrainian_text(text)
    t_no_apos = t_norm.replace("'", "")
    matched = []
    seen_ids = set()
    
    sorted_raions = sorted(ALL_RAIONS.values(), key=lambda r: len(r['name_ua']), reverse=True)
    
    for r in sorted_raions:
        if r['id'] in seen_ids:
            continue
        patterns = [r['name_ua'].lower()] + r.get('aliases', [])
        for p in patterns:
            p_norm = normalize_ukrainian_text(p)
            p_no_apos = p_norm.replace("'", "")
            pat1 = r'(?<![а-яіїєґa-z0-9])' + re.escape(p_norm)
            pat2 = r'(?<![а-яіїєґa-z0-9])' + re.escape(p_no_apos)
            if re.search(pat1, t_norm) or (len(p_no_apos) >= 4 and re.search(pat2, t_no_apos)):
                matched.append(r)
                seen_ids.add(r['id'])
                break
    return matched
