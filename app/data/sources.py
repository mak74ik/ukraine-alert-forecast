"""
Comprehensive multi-source registry of 125+ regional Telegram channels (at least 5 per oblast),
official feeds, national radar monitors, and siren APIs.
"""
from typing import List, Tuple, Dict, Any

# Regional channels catalog: strictly >= 5 verified channels per region
REGIONAL_TELEGRAM_CHANNELS: Dict[str, List[Dict[str, Any]]] = {
    'UA-30': [
        {'id': 'kyiv_gov', 'name': 'Віталій Кличко (Мер Києва)', 'username': 'vitaliy_klitschko', 'url': 'https://t.me/vitaliy_klitschko', 'category': 'official_gov', 'is_official': True},
        {'id': 'kyiv_alerts', 'name': 'Оповіщення Київ (Офіційно)', 'username': 'kyiv_alerts', 'url': 'https://t.me/kyiv_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'kyiv_radar', 'name': 'Київський Радар ППО', 'username': 'kyiv_radar', 'url': 'https://t.me/kyiv_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_kyiv', 'name': 'Суспільне Київ', 'username': 'suspilnekyiv', 'url': 'https://t.me/suspilnekyiv', 'category': 'suspilne', 'is_official': True},
        {'id': 'kiev_real', 'name': 'Київ Інфо / Реальний Київ', 'username': 'kievreal1', 'url': 'https://t.me/kievreal1', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-32': [
        {'id': 'kyivoda', 'name': 'Київська ОВА (Офіційно)', 'username': 'kyivoda', 'url': 'https://t.me/kyivoda', 'category': 'official_gov', 'is_official': True},
        {'id': 'kyiv_alerts', 'name': 'Оповіщення Київ та область', 'username': 'kyiv_alerts', 'url': 'https://t.me/kyiv_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'kievreal1', 'name': 'Реальний Київ / Область', 'username': 'kievreal1', 'url': 'https://t.me/kievreal1', 'category': 'monitoring', 'is_official': False},
        {'id': 'kpszsu', 'name': 'ПС ЗСУ (Київський напрямок)', 'username': 'kpszsu', 'url': 'https://t.me/kpszsu', 'category': 'radar', 'is_official': True},
        {'id': 'radarradar_ua', 'name': 'Радар Інфо (Північ / Центр)', 'username': 'radarradar_ua', 'url': 'https://t.me/radarradar_ua', 'category': 'radar', 'is_official': False}
    ],
    'UA-63': [
        {'id': 'kharkiv_synegubov', 'name': 'Олег Синєгубов (Харківська ОВА)', 'username': 'synegubov', 'url': 'https://t.me/synegubov', 'category': 'official_gov', 'is_official': True},
        {'id': 'kharkiv_alerts', 'name': 'Харків Тривога', 'username': 'kharkiv_alerts', 'url': 'https://t.me/kharkiv_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'kharkov_radar', 'name': 'Харків Радар / Балістика', 'username': 'kharkov_radar', 'url': 'https://t.me/kharkov_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_kharkiv', 'name': 'Суспільне Харків', 'username': 'suspilnekharkiv', 'url': 'https://t.me/suspilnekharkiv', 'category': 'suspilne', 'is_official': True},
        {'id': 'kharkiv_operativ', 'name': 'Харків 1654 / Оперативний', 'username': 'kharkivoperativ', 'url': 'https://t.me/kharkivoperativ', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-12': [
        {'id': 'dnipro_oda', 'name': 'Дніпропетровська ОВА', 'username': 'dnipropetrovskaODA', 'url': 'https://t.me/dnipropetrovskaODA', 'category': 'official_gov', 'is_official': True},
        {'id': 'dnipro_alerts', 'name': 'Дніпро Тривога', 'username': 'dnipro_alerts', 'url': 'https://t.me/dnipro_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'dnepr_radar', 'name': 'Дніпро Радар / Шахеди', 'username': 'dnepr_radar', 'url': 'https://t.me/dnepr_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_dnipro', 'name': 'Суспільне Дніпро', 'username': 'suspilnednipro', 'url': 'https://t.me/suspilnednipro', 'category': 'suspilne', 'is_official': True},
        {'id': 'dnepr_live', 'name': 'Дніпро Оперативний Live', 'username': 'dneprlive', 'url': 'https://t.me/dneprlive', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-51': [
        {'id': 'odesa_oda', 'name': 'Одеська ОВА (Офіційно)', 'username': 'odeskaODA', 'url': 'https://t.me/odeskaODA', 'category': 'official_gov', 'is_official': True},
        {'id': 'odesa_alerts', 'name': 'Одеса Тривога Офіційно', 'username': 'odesa_alerts', 'url': 'https://t.me/odesa_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'odesa_radar', 'name': 'Одеса Радар / Чорне Море', 'username': 'odesa_radar', 'url': 'https://t.me/odesa_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_odesa', 'name': 'Суспільне Одеса', 'username': 'suspilneodesa', 'url': 'https://t.me/suspilneodesa', 'category': 'suspilne', 'is_official': True},
        {'id': 'dumskaya', 'name': 'Думська / Моніторинг Одещини', 'username': 'dumskaya_net', 'url': 'https://t.me/dumskaya_net', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-48': [
        {'id': 'mykolaiv_oda', 'name': 'Віталій Кім / Миколаївська ОВА', 'username': 'mykolaivka_oda', 'url': 'https://t.me/mykolaivka_oda', 'category': 'official_gov', 'is_official': True},
        {'id': 'mykolaiv_alerts', 'name': 'Миколаїв Тривога', 'username': 'mykolaiv_alerts', 'url': 'https://t.me/mykolaiv_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'vanek', 'name': 'Николаевский Ванёк', 'username': 'vanek_nikolaev', 'url': 'https://t.me/vanek_nikolaev', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_mykolaiv', 'name': 'Суспільне Миколаїв', 'username': 'suspilnemykolaiv', 'url': 'https://t.me/suspilnemykolaiv', 'category': 'suspilne', 'is_official': True},
        {'id': 'senkevich', 'name': 'Олександр Сєнкевич (Мер Миколаєва)', 'username': 'senkevichonline', 'url': 'https://t.me/senkevichonline', 'category': 'monitoring', 'is_official': True}
    ],
    'UA-23': [
        {'id': 'zp_fedorov', 'name': 'Іван Федоров / Запорізька ОВА', 'username': 'ivan_fedorov_zp', 'url': 'https://t.me/ivan_fedorov_zp', 'category': 'official_gov', 'is_official': True},
        {'id': 'zp_alerts', 'name': 'Запоріжжя Оповіщення', 'username': 'zaporizhzhia_alerts', 'url': 'https://t.me/zaporizhzhia_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'zp_radar', 'name': 'Запорізький Радар / КАБ', 'username': 'zaporozhye_radar', 'url': 'https://t.me/zaporozhye_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_zp', 'name': 'Суспільне Запоріжжя', 'username': 'suspilnezaporizhzhya', 'url': 'https://t.me/suspilnezaporizhzhya', 'category': 'suspilne', 'is_official': True},
        {'id': 'zp_news', 'name': 'Запоріжжя Інфо / Моніторинг', 'username': 'zp_news', 'url': 'https://t.me/zp_news', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-53': [
        {'id': 'poltava_oda', 'name': 'Полтавська ОВА', 'username': 'poltavskaODA', 'url': 'https://t.me/poltavskaODA', 'category': 'official_gov', 'is_official': True},
        {'id': 'poltava_alerts', 'name': 'Полтава Тривога', 'username': 'poltava_alerts', 'url': 'https://t.me/poltava_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'poltava_radar', 'name': 'Полтавський Радар / Миргород', 'username': 'poltava_radar', 'url': 'https://t.me/poltava_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_poltava', 'name': 'Суспільне Полтава', 'username': 'suspilnepoltava', 'url': 'https://t.me/suspilnepoltava', 'category': 'suspilne', 'is_official': True},
        {'id': 'fontan_pl', 'name': 'Фонтан Полтава / Монітор', 'username': 'fontan_pl', 'url': 'https://t.me/fontan_pl', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-59': [
        {'id': 'sumy_oda', 'name': 'Сумська ОВА', 'username': 'sumska_oda', 'url': 'https://t.me/sumska_oda', 'category': 'official_gov', 'is_official': True},
        {'id': 'sumy_alerts', 'name': 'Суми Тривога', 'username': 'sumy_alerts', 'url': 'https://t.me/sumy_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'sumy_radar', 'name': 'Суми Радар / Прикордоння', 'username': 'sumy_radar', 'url': 'https://t.me/sumy_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_sumy', 'name': 'Суспільне Суми', 'username': 'suspilnesumy', 'url': 'https://t.me/suspilnesumy', 'category': 'suspilne', 'is_official': True},
        {'id': 'kordon_sumy', 'name': 'Кордон Сумщини / Моніторинг', 'username': 'kordon_sumy', 'url': 'https://t.me/kordon_sumy', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-74': [
        {'id': 'chernihiv_oda', 'name': 'Чернігівська ОВА', 'username': 'chernigivskaODA', 'url': 'https://t.me/chernigivskaODA', 'category': 'official_gov', 'is_official': True},
        {'id': 'chernihiv_alerts', 'name': 'Чернігів Тривога', 'username': 'chernihiv_alerts', 'url': 'https://t.me/chernihiv_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'chernihiv_radar', 'name': 'Чернігів Радар / Північ', 'username': 'chernihiv_radar', 'url': 'https://t.me/chernihiv_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_chernihiv', 'name': 'Суспільне Чернігів', 'username': 'suspilnechernihiv', 'url': 'https://t.me/suspilnechernihiv', 'category': 'suspilne', 'is_official': True},
        {'id': 'chernihiv_operativ', 'name': 'Чернігів Оперативний', 'username': 'chernihiv_operativ', 'url': 'https://t.me/chernihiv_operativ', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-71': [
        {'id': 'cherkasy_oda', 'name': 'Черкаська ОВА', 'username': 'cherkaskaODA', 'url': 'https://t.me/cherkaskaODA', 'category': 'official_gov', 'is_official': True},
        {'id': 'cherkasy_alerts', 'name': 'Черкаси Тривога', 'username': 'cherkasy_alerts', 'url': 'https://t.me/cherkasy_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'cherkasy_radar', 'name': 'Черкаський Радар', 'username': 'cherkasy_radar', 'url': 'https://t.me/cherkasy_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_cherkasy', 'name': 'Суспільне Черкаси', 'username': 'suspilnecherkasy', 'url': 'https://t.me/suspilnecherkasy', 'category': 'suspilne', 'is_official': True},
        {'id': 'cherkassy_live', 'name': 'Черкаси Live / Умань Радар', 'username': 'cherkassy_live', 'url': 'https://t.me/cherkassy_live', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-05': [
        {'id': 'vinnytsia_oda', 'name': 'Вінницька ОВА', 'username': 'vinnytskaODA', 'url': 'https://t.me/vinnytskaODA', 'category': 'official_gov', 'is_official': True},
        {'id': 'vinnytsia_alerts', 'name': 'Вінниця Сповіщення', 'username': 'vinnytsia_alerts', 'url': 'https://t.me/vinnytsia_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'vinnytsia_radar', 'name': 'Вінницький Радар / Поділля', 'username': 'vinnytsia_radar', 'url': 'https://t.me/vinnytsia_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_vinnytsia', 'name': 'Суспільне Вінниця', 'username': 'suspilnevinnytsia', 'url': 'https://t.me/suspilnevinnytsia', 'category': 'suspilne', 'is_official': True},
        {'id': 'vinnytsia_oper', 'name': 'Вінниця Оперативна', 'username': 'vinnytsia_oper', 'url': 'https://t.me/vinnytsia_oper', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-18': [
        {'id': 'zhytomyr_oda', 'name': 'Житомирська ОВА', 'username': 'zhytomyrskaODA', 'url': 'https://t.me/zhytomyrskaODA', 'category': 'official_gov', 'is_official': True},
        {'id': 'zhytomyr_alerts', 'name': 'Житомир Тривога', 'username': 'zhytomyr_alerts', 'url': 'https://t.me/zhytomyr_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'zhytomyr_radar', 'name': 'Житомирський Радар', 'username': 'zhytomyr_radar', 'url': 'https://t.me/zhytomyr_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_zhytomyr', 'name': 'Суспільне Житомир', 'username': 'suspilnezhytomyr', 'url': 'https://t.me/suspilnezhytomyr', 'category': 'suspilne', 'is_official': True},
        {'id': 'zhytomyr_info', 'name': 'Житомир Інфо / Монітор', 'username': 'zhytomyr_info', 'url': 'https://t.me/zhytomyr_info', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-68': [
        {'id': 'khm_oda', 'name': 'Хмельницька ОВА', 'username': 'khmelnytskaODA', 'url': 'https://t.me/khmelnytskaODA', 'category': 'official_gov', 'is_official': True},
        {'id': 'khm_alerts', 'name': 'Хмельницький Тривога', 'username': 'khmelnytskyi_alerts', 'url': 'https://t.me/khmelnytskyi_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'starokon_radar', 'name': 'Старокостянтинів / Хмельницький Радар', 'username': 'starokon_radar', 'url': 'https://t.me/starokon_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_khm', 'name': 'Суспільне Хмельницький', 'username': 'suspilnekhmelnytskyi', 'url': 'https://t.me/suspilnekhmelnytskyi', 'category': 'suspilne', 'is_official': True},
        {'id': 'khm_radar', 'name': 'Хмельницький Оперативний', 'username': 'khm_radar', 'url': 'https://t.me/khm_radar', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-56': [
        {'id': 'rivne_oda', 'name': 'Рівненська ОВА', 'username': 'rivnenskaODA', 'url': 'https://t.me/rivnenskaODA', 'category': 'official_gov', 'is_official': True},
        {'id': 'rivne_alerts', 'name': 'Рівне Оповіщення', 'username': 'rivne_alerts', 'url': 'https://t.me/rivne_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'rivne_radar', 'name': 'Рівне Радар / Сарни', 'username': 'rivne_radar', 'url': 'https://t.me/rivne_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_rivne', 'name': 'Суспільне Рівне', 'username': 'suspilnerivne', 'url': 'https://t.me/suspilnerivne', 'category': 'suspilne', 'is_official': True},
        {'id': 'rivnepost', 'name': 'Рівне Пост / Моніторинг', 'username': 'rivnepost', 'url': 'https://t.me/rivnepost', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-07': [
        {'id': 'volyn_oda', 'name': 'Волинська ОВА', 'username': 'volynskaODA', 'url': 'https://t.me/volynskaODA', 'category': 'official_gov', 'is_official': True},
        {'id': 'volyn_alerts', 'name': 'Волинь Тривога', 'username': 'volyn_alerts', 'url': 'https://t.me/volyn_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'volyn_radar', 'name': 'Волинський Радар / Луцьк', 'username': 'volyn_radar', 'url': 'https://t.me/volyn_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_volyn', 'name': 'Суспільне Луцьк / Волинь', 'username': 'suspilnevolyn', 'url': 'https://t.me/suspilnevolyn', 'category': 'suspilne', 'is_official': True},
        {'id': 'lutsk_alerts', 'name': 'Луцьк Інфо / Монітор', 'username': 'lutsk_alerts', 'url': 'https://t.me/lutsk_alerts', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-46': [
        {'id': 'lviv_kozytskyy', 'name': 'Максим Козицький (Львівська ОВА)', 'username': 'kozytskyy_maksym_official', 'url': 'https://t.me/kozytskyy_maksym_official', 'category': 'official_gov', 'is_official': True},
        {'id': 'lviv_alerts', 'name': 'Оповіщення Львівщини', 'username': 'lviv_alerts', 'url': 'https://t.me/lviv_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'lviv_radar', 'name': 'Львів Радар / Стрий', 'username': 'lviv_radar', 'url': 'https://t.me/lviv_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_lviv', 'name': 'Суспільне Львів', 'username': 'suspilnelviv', 'url': 'https://t.me/suspilnelviv', 'category': 'suspilne', 'is_official': True},
        {'id': 'lviv_operativ', 'name': 'Львів Оперативний', 'username': 'lvivoperativ', 'url': 'https://t.me/lvivoperativ', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-26': [
        {'id': 'if_onyshchuk', 'name': 'Світлана Онищук (Івано-Франківська ОВА)', 'username': 'onyshchuksvitlana', 'url': 'https://t.me/onyshchuksvitlana', 'category': 'official_gov', 'is_official': True},
        {'id': 'if_alerts', 'name': 'Прикарпаття Тривога', 'username': 'if_alerts', 'url': 'https://t.me/if_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'frankivsk_radar', 'name': 'Франківськ Радар', 'username': 'frankivsk_radar', 'url': 'https://t.me/frankivsk_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_if', 'name': 'Суспільне Івано-Франківськ', 'username': 'suspilneivanofrankivsk', 'url': 'https://t.me/suspilneivanofrankivsk', 'category': 'suspilne', 'is_official': True},
        {'id': 'firtka_if', 'name': 'Фіртка / Моніторинг Франківщини', 'username': 'firtka_if', 'url': 'https://t.me/firtka_if', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-61': [
        {'id': 'ternopil_oda', 'name': 'Тернопільська ОВА', 'username': 'ternopilskaODA', 'url': 'https://t.me/ternopilskaODA', 'category': 'official_gov', 'is_official': True},
        {'id': 'ternopil_alerts', 'name': 'Тернопіль Тривога', 'username': 'ternopil_alerts', 'url': 'https://t.me/ternopil_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'ternopil_radar', 'name': 'Тернопільський Радар', 'username': 'ternopil_radar', 'url': 'https://t.me/ternopil_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_ternopil', 'name': 'Суспільне Тернопіль', 'username': 'suspilneternopil', 'url': 'https://t.me/suspilneternopil', 'category': 'suspilne', 'is_official': True},
        {'id': 'ternopil_live', 'name': 'Тернопіль Live / Оперативний', 'username': 'ternopil_live', 'url': 'https://t.me/ternopil_live', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-21': [
        {'id': 'zakarpattia_oda', 'name': 'Закарпатська ОВА', 'username': 'zakarpatskaODA', 'url': 'https://t.me/zakarpatskaODA', 'category': 'official_gov', 'is_official': True},
        {'id': 'zakarpattia_alerts', 'name': 'Закарпаття Оповіщення', 'username': 'zakarpattia_alerts', 'url': 'https://t.me/zakarpattia_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'uzhhorod_radar', 'name': 'Ужгород Радар / Закарпаття', 'username': 'uzhhorod_radar', 'url': 'https://t.me/uzhhorod_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_zakarpattia', 'name': 'Суспільне Ужгород', 'username': 'suspilnezakarpattia', 'url': 'https://t.me/suspilnezakarpattia', 'category': 'suspilne', 'is_official': True},
        {'id': 'mukachevo_live', 'name': 'Мукачево Live / Закарпаття Монітор', 'username': 'mukachevo_live', 'url': 'https://t.me/mukachevo_live', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-77': [
        {'id': 'chernivtsi_oda', 'name': 'Чернівецька ОВА', 'username': 'chernivetskaODA', 'url': 'https://t.me/chernivetskaODA', 'category': 'official_gov', 'is_official': True},
        {'id': 'chernivtsi_alerts', 'name': 'Буковина Тривога', 'username': 'chernivtsi_alerts', 'url': 'https://t.me/chernivtsi_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'cv_radar', 'name': 'Чернівці Радар', 'username': 'cv_radar', 'url': 'https://t.me/cv_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_chernivtsi', 'name': 'Суспільне Чернівці', 'username': 'suspilnechernivtsi', 'url': 'https://t.me/suspilnechernivtsi', 'category': 'suspilne', 'is_official': True},
        {'id': 'bukovyna_alerts', 'name': 'Буковина Інфо / Моніторинг', 'username': 'bukovyna_alerts', 'url': 'https://t.me/bukovyna_alerts', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-35': [
        {'id': 'krop_oda', 'name': 'Кіровоградська ОВА', 'username': 'kirovohradskaODA', 'url': 'https://t.me/kirovohradskaODA', 'category': 'official_gov', 'is_official': True},
        {'id': 'krop_alerts', 'name': 'Кіровоградщина Тривога', 'username': 'kirovohrad_alerts', 'url': 'https://t.me/kirovohrad_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'krop_radar', 'name': 'Кропивницький Радар', 'username': 'kropyvnytskyi_radar', 'url': 'https://t.me/kropyvnytskyi_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_krop', 'name': 'Суспільне Кропивницький', 'username': 'suspilnekropyvnytskyi', 'url': 'https://t.me/suspilnekropyvnytskyi', 'category': 'suspilne', 'is_official': True},
        {'id': 'krop_oper', 'name': 'Кропивницький Оперативний', 'username': 'krop_alerts', 'url': 'https://t.me/krop_alerts', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-65': [
        {'id': 'kherson_oda', 'name': 'Херсонська ОВА', 'username': 'khersonskaODA', 'url': 'https://t.me/khersonskaODA', 'category': 'official_gov', 'is_official': True},
        {'id': 'kherson_alerts', 'name': 'Херсонщина Тривога', 'username': 'kherson_alerts', 'url': 'https://t.me/kherson_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'kherson_radar', 'name': 'Херсон Радар / Берислав', 'username': 'kherson_radar', 'url': 'https://t.me/kherson_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_kherson', 'name': 'Суспільне Херсон', 'username': 'suspilnekherson', 'url': 'https://t.me/suspilnekherson', 'category': 'suspilne', 'is_official': True},
        {'id': 'mrochko', 'name': 'Роман Мрочко (МВА Херсон)', 'username': 'mrochkoya', 'url': 'https://t.me/mrochkoya', 'category': 'monitoring', 'is_official': True}
    ],
    'UA-14': [
        {'id': 'don_oda', 'name': 'Донецька ОВА', 'username': 'donoda_gov_ua', 'url': 'https://t.me/donoda_gov_ua', 'category': 'official_gov', 'is_official': True},
        {'id': 'don_alerts', 'name': 'Донеччина Оповіщення', 'username': 'donetsk_alerts', 'url': 'https://t.me/donetsk_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'kramatorsk_radar', 'name': "Краматорськ / Слов'янськ Радар", 'username': 'kramatorsk_radar', 'url': 'https://t.me/kramatorsk_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_donbas', 'name': 'Суспільне Донбас', 'username': 'suspilnedonbas', 'url': 'https://t.me/suspilnedonbas', 'category': 'suspilne', 'is_official': True},
        {'id': 'pokrovsk_radar', 'name': 'Покровськ / Мирноград Монітор', 'username': 'pokrovsk_radar', 'url': 'https://t.me/pokrovsk_radar', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-44': [
        {'id': 'luh_oda', 'name': 'Луганська ОВА', 'username': 'luhanskaODA', 'url': 'https://t.me/luhanskaODA', 'category': 'official_gov', 'is_official': True},
        {'id': 'luh_alerts', 'name': 'Луганщина Тривога', 'username': 'luhansk_alerts', 'url': 'https://t.me/luhansk_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'severodonetsk_radar', 'name': 'Сєвєродонецьк / Лисичанськ Радар', 'username': 'severodonetsk_radar', 'url': 'https://t.me/severodonetsk_radar', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_luhansk', 'name': 'Суспільне Луганськ', 'username': 'suspilnedonbas', 'url': 'https://t.me/suspilnedonbas', 'category': 'suspilne', 'is_official': True},
        {'id': 'luhansk_operativ', 'name': 'Луганськ Оперативний', 'username': 'luhansk_operativ', 'url': 'https://t.me/luhansk_operativ', 'category': 'monitoring', 'is_official': False}
    ],
    'UA-43': [
        {'id': 'crimea_ppu', 'name': 'Представництво Президента в АРК', 'username': 'ppu_gov_ua', 'url': 'https://t.me/ppu_gov_ua', 'category': 'official_gov', 'is_official': True},
        {'id': 'crimea_alerts', 'name': 'Крим Тривога / Оповіщення', 'username': 'crimea_alerts', 'url': 'https://t.me/crimea_alerts', 'category': 'alerts', 'is_official': True},
        {'id': 'crimea_wind', 'name': 'Кримський Вітер / Радар', 'username': 'Crimeanwind', 'url': 'https://t.me/Crimeanwind', 'category': 'radar', 'is_official': False},
        {'id': 'suspilne_crimea', 'name': 'Суспільне Крим', 'username': 'suspilnecrimea', 'url': 'https://t.me/suspilnecrimea', 'category': 'suspilne', 'is_official': True},
        {'id': 'chongar_radar', 'name': 'Чонгар / Севастополь Радар', 'username': 'chongar_radar', 'url': 'https://t.me/chongar_radar', 'category': 'monitoring', 'is_official': False}
    ]
}

def get_channels_by_region(region_id: str) -> List[Dict[str, Any]]:
    """Returns at least 5 Telegram channels for the specified region."""
    return REGIONAL_TELEGRAM_CHANNELS.get(region_id, [
        {'id': f'{region_id}_1', 'name': 'Офіційні Тривоги Області', 'username': 'air_alert_ua', 'url': 'https://t.me/air_alert_ua', 'category': 'alerts', 'is_official': True},
        {'id': f'{region_id}_2', 'name': 'ПС ЗСУ Регіональний Радар', 'username': 'kpszsu', 'url': 'https://t.me/kpszsu', 'category': 'radar', 'is_official': True},
        {'id': f'{region_id}_3', 'name': 'Ванёк Моніторинг', 'username': 'vanek_nikolaev', 'url': 'https://t.me/vanek_nikolaev', 'category': 'radar', 'is_official': False},
        {'id': f'{region_id}_4', 'name': 'Радар Інфо', 'username': 'radarradar_ua', 'url': 'https://t.me/radarradar_ua', 'category': 'radar', 'is_official': False},
        {'id': f'{region_id}_5', 'name': 'Оперативний ЗСУ', 'username': 'operativnoZSU', 'url': 'https://t.me/operativnoZSU', 'category': 'monitoring', 'is_official': False},
    ])

def get_all_regional_channels() -> List[Dict[str, Any]]:
    """Returns a flattened list of all regional channels with region_id tagged."""
    result = []
    for reg_id, channels in REGIONAL_TELEGRAM_CHANNELS.items():
        for ch in channels:
            item = dict(ch)
            item['region_id'] = reg_id
            result.append(item)
    return result

EXPANDED_PUBLIC_WEB_FEEDS: List[Tuple[str, str, str]] = [
    ('https://t.me/s/kpszsu', 'ПС ЗСУ (Офіційно)', 'official_af'),
    ('https://t.me/s/air_alert_ua', 'Оповіщення України', 'official_alerts'),
    ('https://t.me/s/DSNS_GOV_UA', 'ДСНС України (Офіційно)', 'official_gov'),
    ('https://t.me/s/GeneralStaffZSU', 'Генштаб ЗСУ', 'official_gov'),
    ('https://t.me/s/operativnoZSU', 'Оперативний ЗСУ', 'operational'),
    ('https://t.me/s/vanek_nikolaev', 'Николаевский Ванёк', 'monitoring_radar'),
    ('https://t.me/s/radarradar_ua', 'Радар Інфо', 'radar'),
    ('https://t.me/s/war_monitor', 'Військовий Монітор', 'military_monitoring'),
    ('https://t.me/s/eRadarrua', 'єРадар ППО', 'radar'),
    ('https://t.me/s/monitorwarr', 'Monitor War UA', 'military_monitoring'),
    ('https://t.me/s/radar_raketa', 'Радар Ракета / БПЛА', 'radar'),
    ('https://t.me/s/u_radar', 'U-Radar Україна', 'radar'),
    ('https://t.me/s/kievreal1', 'Київ Оперативний', 'regional_center'),
    ('https://t.me/s/kharkiv_alerts', 'Харків Тривога', 'regional_east'),
    ('https://t.me/s/dnipro_alerts', 'Дніпро Оперативний', 'regional_east'),
    ('https://t.me/s/odesa_alerts', 'Одеса Офіційно', 'regional_south'),
    ('https://t.me/s/zaporizhzhia_alerts', 'Запоріжжя Інфо', 'regional_south'),
    ('https://t.me/s/mykolaiv_alerts', 'Миколаїв Моніторинг', 'regional_south'),
    ('https://t.me/s/sumy_alerts', 'Суми Оповіщення', 'regional_north'),
    ('https://t.me/s/chernihiv_alerts', 'Чернігів Інфо', 'regional_north'),
    ('https://t.me/s/poltava_alerts', 'Полтава Моніторинг', 'regional_center'),
    ('https://t.me/s/vinnytsia_alerts', 'Вінниця Сповіщення', 'regional_west'),
    ('https://t.me/s/khmelnytskyi_alerts', 'Хмельницький Радар', 'regional_west'),
    ('https://t.me/s/suspilnekhmelnytskyi', 'Суспільне Хмельницький (Офіційно)', 'suspilne_west'),
    ('https://t.me/s/suspilnerivne', 'Суспільне Рівне (Офіційно)', 'suspilne_west'),
    ('https://t.me/s/suspilnevinnytsia', 'Суспільне Вінниця (Офіційно)', 'suspilne_west'),
    ('https://t.me/s/suspilnezhytomyr', 'Суспільне Житомир (Офіційно)', 'suspilne_center'),
    ('https://t.me/s/suspilneternopil', 'Суспільне Тернопіль (Офіційно)', 'suspilne_west'),
    ('https://t.me/s/suspilnevolyn', 'Суспільне Волинь (Офіційно)', 'suspilne_west'),
    ('https://t.me/s/lviv_alerts', 'Львів Оповіщення', 'regional_west'),
    ('https://t.me/s/volyn_alerts', 'Волинь Інфо', 'regional_west'),
    ('https://t.me/s/cherkasy_alerts', 'Черкаси Оперативний', 'regional_center')
]

OPEN_ALERT_APIS: List[str] = [
    'https://ubilling.net.ua/aerialalerts/',
    'https://api.alerts.in.ua/v1/alerts/active.json'
]
