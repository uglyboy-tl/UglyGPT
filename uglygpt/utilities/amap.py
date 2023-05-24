import requests

from uglygpt.base import config, logger, Fore
class AMap():
    def __init__(self):
        self.key:str = config.amap_api_key
        city_info = self._get("https://restapi.amap.com/v3/ip", {"key":self.key})
        self.city:str = city_info["city"]
        self.adcode:str = city_info["adcode"]

    def _get(self,url:str,params:dict):
        reponse = requests.get(url,params=params).json()
        if reponse["status"] == "1":
            return reponse
        else:
            logger.error(reponse["info"])
            raise Exception(reponse["info"])

    def _parse_poi(self, poi:dict) -> str:
        result = poi["name"] + "[" + poi["type"] + "]{距离: " + str(poi["distance"]) + "m"
        if 'biz_ext' in poi.keys():
            if 'rating' in poi['biz_ext'].keys():
                result += ", 评分: " + str(poi['biz_ext']['rating'])
            if 'cost' in poi['biz_ext'].keys() and poi['biz_ext']['cost'] != []:
                result += ", 平均消费: " + str(poi['biz_ext']['cost'])
            if 'open_time' in poi['biz_ext'].keys() and poi['biz_ext']['open_time'] != []:
                result += ", 营业时间: " + str(poi['biz_ext']['open_time'])
        result += "}"
        return result

    def get(self, name:str, types=[]):
        url = "https://restapi.amap.com/v3/place/text"
        params = {"key":self.key, "keywords":name, "city":self.city, "citylimit":True, "types":"|".join(types)}
        pois = self._get(url,params)["pois"]
        default_poi = pois[0]
        return default_poi

    def around(self, location:str, types=["050000","060200","080600","110000"], radius:int=1000):
        url = "https://restapi.amap.com/v3/place/around"
        params = {"key":self.key, "location":location, "radius":radius, "types":"|".join(types), "page_size":15, "show_fields":"business_area,tel,rating,cost"}
        pois = self._get(url,params)["pois"]
        result = []
        for poi in pois:
            result.append(self._parse_poi(poi))
        return result

    def weather(self, adcode:str=None, realtime:bool=False):
        url = "https://restapi.amap.com/v3/weather/weatherInfo"
        if adcode is None:
            adcode = self.adcode
        params = {"key":self.key, "city":adcode}
        if realtime:
            params["extensions"] = "base"
        else:
            params["extensions"] = "all"
        return self._get(url,params)