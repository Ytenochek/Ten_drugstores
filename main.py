from io import BytesIO
import requests
from PIL import Image
from counter import *

search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

text = input("Введите адрес: ")

search_params = {
    "apikey": api_key,
    "text": text,
    "lang": "ru_RU",
}

response = requests.get(search_api_server, params=search_params)
if not response:
    print("Место не найдено")
else:
    json_response = response.json()

    place = json_response["features"]
    if place:
        place = place[0]
        point = place["geometry"]["coordinates"]
        org_point1 = "{0},{1}".format(point[0], point[1])

        map_params = {
            "apikey": api_key,
            "text": "аптека",
            "lang": "ru_RU",
            "type": "biz",
            "ll": ",".join(map(str, point)),
        }

        map_api_server = "https://search-maps.yandex.ru/v1/"
        response = requests.get(map_api_server, params=map_params)

        json_response = response.json()
        places = json_response["features"][:10]
        spn = [[], []]
        pt = []

        for place in places:
            point = place["geometry"]["coordinates"]
            size = json_response["properties"]["ResponseMetaData"]["SearchResponse"][
                "boundedBy"
            ]
            if not spn[0]:
                spn = size.copy()
            else:
                spn[0][0] = min(spn[0][0], size[0][0])
                spn[0][1] = min(spn[0][1], size[0][1])
                spn[1][0] = max(spn[1][0], size[1][0])
                spn[1][1] = max(spn[1][1], size[1][1])

            if "Hours" in place["properties"]["CompanyMetaData"].keys():
                if (
                    "TwentyFourHours"
                    in place["properties"]["CompanyMetaData"]["Hours"][
                        "Availabilities"
                    ][0]
                    and place["properties"]["CompanyMetaData"]["Hours"][
                        "Availabilities"
                    ][0]["TwentyFourHours"]
                ):
                    pt.append(f"{point[0]},{point[1]},pm2dgm")
                else:
                    pt.append(f"{point[0]},{point[1]},pm2dbm")
            else:
                pt.append(f"{point[0]},{point[1]},pm2grm")
        spn = spn_counter(spn)

        map_params = {
            "spn": ",".join(spn),
            "l": "map",
            "pt": "~".join(pt),
        }

        map_api_server = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params=map_params)

        Image.open(BytesIO(response.content)).show()
    else:
        print("Место не найдено")
