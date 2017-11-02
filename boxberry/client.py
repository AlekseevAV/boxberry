# coding: utf-8
from __future__ import unicode_literals

import json

import requests

from .utils import decimal_default
from .exceptions import BoxberryAPIError


class BoxberryAPI(object):

    def __init__(self, token, endpoint, request_timeout=10):
        """
        :param token: токен личного кабинета
        :param endpoint: url адрес API
        :param request_timeout: таймаут запросов к API
        """
        self._token = token
        self._endpoint = endpoint
        self.request_timeout = request_timeout

    def _request(self, api_method, request_method='get', params=None, data=None):

        common_data = dict(
            method=api_method,
            token=self._token
        )

        if request_method == 'get':
            params = params or {}
            params.update(common_data)
        elif request_method == 'post':
            data = data or {}
            data.update(common_data)
        else:
            raise ValueError('Unknown request method "{}"'.format(request_method))

        request_method = getattr(requests, request_method)

        try:
            response = request_method(self._endpoint, params=params, data=data, timeout=self.request_timeout)
        except requests.RequestException as e:
            raise BoxberryAPIError('Http error: %s', e)

        try:
            js = json.loads(response.content)
        except ValueError:
            raise BoxberryAPIError('Invalid response, bb down? %s', response.content[:100])

        self._raise_exception_if_error(js_data=js)

        return js

    @staticmethod
    def _raise_exception_if_error(js_data):
        if 'err' in js_data:
            raise BoxberryAPIError(js_data['err'])
        if isinstance(js_data, list):
            for item in js_data:
                if 'err' in item:
                    raise BoxberryAPIError(item['err'])

    def list_cities(self):
        """
        Позволяет получить список городов, в которых есть пункты выдачи
        """
        return self._request('ListCities')

    def list_cities_full(self):
        """
        Позволяет получить список городов, в которых осуществляется доставка Boxberry
        """
        return self._request('ListCitiesFull')

    def list_points(self, code=None, prepaid=None):
        """
        Позволяет получить информацию о всех точках выдачи заказов.

        При использовании дополнительного параметра ("code" код города в boxberry) позволяет выбрать ПВЗ только в
        заданном городе.
        По умолчанию возвращается список точек с возможностью оплаты при получении заказа
        (параметр "OnlyPrepaidOrders"=No).
        Если вам необходимо увидеть точки, работающие с любым типом посылок, передайте параметр "prepaid" равный 1.
        """

        params = {}
        if code:
            params['CityCode'] = code
        if prepaid:
            params['prepaid'] = prepaid

        return self._request('ListPoints', params=params)

    def list_points_short(self, city_code=None):
        """
        Позволяет получить коды всех ПВЗ, либо для отдельно взятого города при указании city_code,
        а так же дату последнего изменения.

        :param city_code: код города
        """

        params = {}
        if city_code:
            params['CityCode'] = city_code

        return self._request('ListPointsShort', params=params)

    def list_zips(self):
        """
        Позволяет получить список почтовых индексов, для которых возможна курьерская доставка.

        Внимание! объем возвращаемых данных около 14 mb.
        """
        return self._request('ListZips')

    def zip_check(self, zip_code):
        """
        Позволяет получить информацию о возможности осуществления курьерской доставки в заданном индексе.

        :param zip_code: почтовый код для которого осуществляется проверка
        """
        return self._request('ZipCheck', params={'zip': zip_code})

    def list_statuses(self, tracking_number):
        """
        Получить информацию о статусах посылки

        :param tracking_number: код отслеживания заказа
        """
        return self._request('ListStatuses', params={'ImId': tracking_number})

    def list_statuses_full(self, tracking_number):
        """
        Позволяет получить полную информацию о статусах посылки.

        :param tracking_number: код отслеживания заказа
        """
        return self._request('ListStatusesFull', params={'ImId': tracking_number})

    def list_services(self, tracking_number):
        """
        Позволяет получить перечень и стоимость оказанных услуг по отправлению.

        :param tracking_number: код отслеживания заказа
        """
        return self._request('ListServices', params={'ImId': tracking_number})

    def courier_list_cities(self):
        """
        Позволяет получить список городов в которых осуществляется курьерская доставка
        """
        return self._request('CourierListCities')

    def delivery_costs(self, weight=None, target=None, order_sum=None, delivery_sum=None, target_start=None,
                       height=None, width=None, depth=None, zip_code=None, pay_sum=None):
        """
        Данный метод позволяет узнать стоимость доставки посылки до ПВЗ или клиента(курьерская доставка).

        :param weight: вес посылки в граммах,
        :param target: код ПВЗ,
        :param order_sum: cтоимость товаров без учета стоимости доставки,
        :param delivery_sum: заявленная ИМ стоимость доставки,
        :param target_start: код пункта приема посылок,
        :param height: высота коробки (см),
        :param width: ширина коробки (см),
        :param depth: глубина коробки (см),
        :param zip_code: индекс города для курьерской доставки
        :param pay_sum: сумма к оплате
        """
        params = {
            'weight': weight,
            'target': target,
            'ordersum': order_sum,
            'deliverysum': delivery_sum,
            'targetstart': target_start,
            'height': height,
            'width': width,
            'depth': depth,
            'zip': zip_code,
            'paysum': pay_sum,
        }

        return self._request('DeliveryCosts', params=params)

    def points_for_parcels(self):
        """
        Позволяет получить список точек приёма посылок.
        """
        return self._request('PointsForParcels')

    def points_by_post_code(self, zip_code):
        """
        Метод позволяет получить код ПВЗ из Boxberry по индексу города.

        :param zip_code: почтовый код для которого осуществляется проверка
        """
        return self._request('PointsForParcels', params={'zip': zip_code})

    def points_description(self, code, with_photo=False):
        """
        Метод позволяет получить всю информацию по пункту выдачи, включая фотографии.

        :param code: код ПВЗ
        :param with_photo: если True, то будет возвращен массив полноразмерных изображений ПВЗ в base64
        """

        params = {'code': code}
        if with_photo:
            params['photo'] = 1

        return self._request('PointsForParcels', params=params)

    def parsel_create_or_update(self, delivery_data):
        """
        Сокращения:
            ЗП – заказ получателя,
            ИМ – интернет магазин,
            БД – база данных,
            ПВЗ – пункт выдачи заказов,
            КД – курьерская доставка

        Параметры (http://api.boxberry.de/?act=info&sub=api_info_lk):
            Общая информация о посылке:
                updateByTrack - Трекинг-код ранее созданной посылки (Если параметр updateByTrack будет не пустым,
                                считается что вы хотите обновить ранее созданную посылку)
                order_id -      ID заказа в ИМ
                PalletNumber -  Номер палеты
                price -         Общая (объявленная) стоимость ЗП, руб.
                payment_sum -   Сумма к оплате (сумма, которую необходимо взять с получателя), руб
                delivery_sum -  Стоимость доставки
                vid -           Тип доставки (1 – самовывоз (доставка до ПВЗ), 2 – КД (экспресс-доставка до получателя))
            Информация о пункте поступления и пункте выдачи:
                shop:
                    name -  Код ПВЗ, в котором получатель будет забирать ЗП.
                            Заполняется для самовывоза, для КД – оставить пустым.
                    name1 - Код пункта поступления ЗП (код ПВЗ, в который ИМ сдаёт посылки для доставки).
                            Заполняется всегда, не зависимо от вида доставки.
                            Для ИМ, сдающих отправления на ЦСУ Москва заполняется значением 010
            Информация о получателе:
                customer:
                    fio -       ФИО получателя ЗП.
                                Возможные варианты заполнения: «Фамилия Имя Отчество» или «Фамилия Имя» (разделитель –
                                пробел).
                                Внимание, для полностью предоплаченных заказов необходимо указывать Фамилию, Имя и
                                Отчество
                                получателя, т. к. при выдаче на ПВЗ проверяются паспортные данные.
                    phone -     Номер мобильного телефона получателя в формате 9ХХХХХХХХХ (10 цифр, начиная с девятки)
                    phone2 -    Доп. номер телефона
                    email -     E-mail для оповещений
                Наименование юрлица-получателя:
                    name -      Наименование организации
                    address -   Адрес
                    inn -       ИНН
                    kpp -       КПП
                    r_s -       Расчетный счет
                    bank -      Наименование банка
                    kor_s -     Кор. счет
                    bik -       БИК
            Курьерская доставка
                kurdost:
                    index -         Индекс
                    citi -          Город
                    addressp -      Адрес получателя
                    timesfrom1 -    Время доставки, от
                    timesto1 -      Время доставки, до
                    timesfrom2 -    Альтернативное время, от
                    timesto2 -      Альтернативное время, до
                    timep -         Время доставки текстовый формат
                    comentk -       Комментарий
            Блок с информацией по товарным позициям:
                items:
                    id -        Артикул товара в БД
                    name -      Наименование товара
                    UnitName -  Единица измерения
                    nds -       Процент НДС
                    price -     Цена товара
                    quantity -  Количество
                weights:
                    weight -    Вес 1-ого места - Вес первого или единственного тарного места, в граммах.
                                Минимальное значение 5 г, максимальное – 30000 г.
                                weight должно быть заполнено обязательно!
                                weight2, weight3, weight4, weight5 Вес второго и последующих тарных мест, в граммах.
                                Внимание, данные строки добавляются только в случае, если ЗП отправляется
                                двумя и более тарными местами.
                    barcode -   Баркод 1-го места - Внимание Каждый баркод соответствует заполненному весу места.
                                Если у заполненных мест указан хотя бы один баркод, то и остальные необходимо указать.
                    weight2 -   Вес 2-ого места
                    barcode2 -  Баркод 2-го места
                    weight3 -   Вес 3-его места
                    barcode3 -  Баркод 3-го места
                    weight4 -   Вес 4-ого места
                    barcode4 -  Баркод 4-го места
                    weight5 -   Вес 5-ого места
                    barcode5 -  Баркод 5-го места
        """

        return self._request('ParselCreate', request_method='post',
                             data={'sdata': json.dumps(delivery_data, default=decimal_default)})

    def parsel_check(self, tracking_number):
        """
        Позволяет получить ссылку на файл печати этикеток, список штрих-кодов коробок в посылке через запятую (,),
        список штрих-кодов выгруженных коробок в посылке через запятую (,)

        :param tracking_number: код отслеживания заказа
        """
        return self._request('ParselCheck', params={'ImId': tracking_number})

    def parsel_list(self):
        """
        Получить список всех трекинг кодов посылок которые есть в кабинете но не были сформированы в акт.
        """
        return self._request('ParselList')

    def parsel_del(self, tracking_number):
        """
        Позволяет удалить посылку, но только в том случае, если она не была проведена в акте.

        :param tracking_number: код отслеживания заказа
        """
        return self._request('ParselDel', params={'ImId': tracking_number})

    def parsel_story(self, from_date=None, to_date=None):
        """
        Позволяет получить список созданных через API посылок.
        Если не указывать диапазоны дат, то будет возвращена последняя созданная посылка.

        :param from_date: дата "С"
        :type from_date: datetime.datetime
        :param to_date: дата "ДО"
        :type from_date: datetime.datetime
        """

        params = {
            'from': from_date.strftime('%Y%m%d') if from_date else None,
            'to': to_date.strftime('%Y%m%d') if to_date else None,
        }

        return self._request('ParselStory', params=params)

    def parsel_send(self, tracking_numbers):
        """
        Формирует акт передачи посылок в boxberry.

        :param tracking_numbers: коды отслеживания заказов
        :type tracking_numbers: list
        """
        return self._request('ParselSend', params={'ImIds': tracking_numbers})

    def parsel_send_story(self, from_date=None, to_date=None):
        """
        Позволяет получить список созданных через API актов передачи.
        Если не указывать диапазоны дат, то будет возвращен последний созданный акт.

        :param from_date: дата "С"
        :type from_date: datetime.datetime
        :param to_date: дата "ДО"
        :type from_date: datetime.datetime
        """

        params = {
            'from': from_date.strftime('%Y%m%d') if from_date else None,
            'to': to_date.strftime('%Y%m%d') if to_date else None,
        }

        return self._request('ParselSendStory', params=params)

    def orders_balance(self):
        """
        Метод позволяет получить информацию по заказам, по которым уже сформирован акт,
        но они еще не доставлены клиенту.
        """
        return self._request('OrdersBalance')
