from typing import Any

from weather_requester.base import BaseWeatherRequester


class CurrentWeatherRequester(BaseWeatherRequester):
    def request(self, latitude: float, longitude: float) -> dict[str, Any]:
        """Отвечает на вопросы о погоде в данный момент

        Args:
            latitude: Широта (обязательный параметр)
            longitude: Долгота (обязательный параметр)

        Returns:
            Возвращает данные о текущей погоде в виде json
        """
        return super().request(latitude=latitude, longitude=longitude)

    def _prepare_weather_query(self) -> str:
        return '''
        query Weather($latitude: Float!, $longitude: Float!) {
          weatherByPoint(request: { lat: $latitude, lon: $longitude }) {
            now {
              temperature
            }
          }
        }
        '''
