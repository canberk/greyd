import json
import requests

request_map_api = requests.get(
            'http://maps.googleapis.com/maps/api/geocode/json?latlng={}&sensor=true'
            .format("40.587945,31.453287"))
map_json_parse = json.loads(request_map_api.text)
try:
    for i in range(10):
        result_level = map_json_parse["results"][0]["address_components"][i]["types"][0]
        if result_level == "administrative_area_level_1":
            result_city = map_json_parse["results"][0]["address_components"][i]["long_name"]
            break
except IndexError:
    result_city = ''
print(result_city)