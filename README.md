# Boxberry API клиент

Клиент для работы с API Boxberry

### Установка


    pip install boxberry

или из исходников:

    pip install git+https://github.com/AlekseevAV/boxberry
    

### Использование

    from boxberry.client import BoxberryAPI

    boxberry_api = BoxberryAPI(token='test_token', endpoint='https://test.boxberry.de/json.php')
    boxberry_api.points_for_parcels()
