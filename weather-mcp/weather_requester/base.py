import abc
from typing import Any

import requests


class BaseWeatherRequester(abc.ABC):
    def __init__(self, api_key: str):
        self._api_key = api_key

    def request(self, latitude: float, longitude: float) -> dict[str, Any]:
        response = requests.post(
            url='https://api.weather.yandex.ru/graphql/query',
            headers={
                'X-Yandex-Weather-Key': self._api_key,
            },
            json={
                'query': self._prepare_weather_query(),
                'variables': {
                    'latitude': latitude,
                    'longitude': longitude,
                },
            },
        )

        return response.json()

    @abc.abstractmethod
    def _prepare_weather_query(self) -> str:
        ...
