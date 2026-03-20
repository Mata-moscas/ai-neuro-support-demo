from typing import Any

from weather_requester.base import BaseWeatherRequester


class ForecastForTwoDaysRequester(BaseWeatherRequester):
    def request(self, latitude: float, longitude: float) -> dict[str, Any]:
        """Предсказывает погоду на ближайшие 2 дня

        Args:
            latitude: Широта (обязательный параметр)
            longitude: Долгота (обязательный параметр)

        Returns:
            Возвращает данные с прогнозом погоды на ближайшие 2 дня в виде json
        """
        return super().request(latitude=latitude, longitude=longitude)

    def _prepare_weather_query(self) -> str:
        return '''
        query Weather($latitude: Float!, $longitude: Float!) {
          weatherByPoint(request: { lat: $latitude, lon: $longitude }) {
            forecast {
              days(limit: 2) {
                time
                sunriseTime
                sunsetTime
                parts {
                  morning {
                    avgTemperature
                  }
                  day {
                    avgTemperature
                  }
                  evening {
                    avgTemperature
                  }
                  night {
                    avgTemperature
                  }
                }
              }
            }
          }
        }
        '''
