from enum import Enum


class RequestType(Enum):
    REUSABLE = "Многоразовая"
    DISPOSABLE = "Одноразовая"


class Value(Enum):
    DEFAULT = 1


class RequestStatus(Enum):
    APPROVE = "Согласование"
    ALLOWED = "Одобрена"
    REJECTED = "Отклонена"
    WITHDRAWN = "Отозвана"
    CONSIDERATION = "Рассмотрение"
    CLOSED = "Закрыта"
    PASSAPPROVAL = "Прошла согласование"
    UNPASSAPPROVAL = "Не прошла согласование"


class PassageReportsMode(str, Enum):
    CARS = "Автомобили"
    VISITORS = "Посетители"
    SPEC_TRANSPORT = "Спецтранспорт"
    SEARCH_CAR = "ПОИСК"
    SEARCH_VISITOR = "ПОИСК"
    SEARCH_SPECTRANSPORT = "ПОИСК"


class OnTerritoryMode(str, Enum):
    CARS = "Автомобили"
    SPEC_TRANSPORT = "Спецтранспорт"


class Scopes(Enum):
    SUPERUSER = "Суперпользователь"
    ADMIN = "Администратор"
    LIMITED_ADMIN = "Ограниченное администрирование"
    REQUESTER = "Заявитель"
    MONITORING = "Охрана"
