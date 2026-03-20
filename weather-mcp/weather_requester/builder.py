from weather_requester.base import BaseWeatherRequester
from weather_requester.current_weather import CurrentWeatherRequester
from weather_requester.forecast_for_two_days import ForecastForTwoDaysRequester


def build_request_type_to_requester(api_key: str) -> dict[str, BaseWeatherRequester]:
    return {
        'current_weather': CurrentWeatherRequester(api_key=api_key),
        'forecast_for_two_days': ForecastForTwoDaysRequester(api_key=api_key),
    }
