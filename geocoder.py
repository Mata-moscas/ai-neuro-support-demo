import os
import requests
import traceback


def handler(event, context):
    print('event: ', event)  # debug logging

    try:
        user_address = event.get('address')
        if user_address is None:
            return {
                'statusCode': 400,
                'body': 'Parameter "address" is required',
            }


        geo_api_key = os.getenv('GEO_API_KEY')

        response = requests.get(
            url=(
                f'https://geocode-maps.yandex.ru/v1/?'
                f'apikey={geo_api_key}&'
                f'geocode={user_address}&'
                f'format=json'
            ),
        )

        try:
            response.raise_for_status()

            return {
                'statusCode': response.status_code,
                'body': response.json(),
            }
        except requests.exceptions.RequestException:
            return {
                'statusCode': response.status_code,
                'body': traceback.format_exc(),
            }
    except:
        return {
            'statusCode': 500,
            'body': traceback.format_exc(),
        }
