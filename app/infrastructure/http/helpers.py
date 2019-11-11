from typing import Optional

from geoip import geolite2


def get_current_country_by_ip(ip_address: str) -> Optional[str]:
    match = geolite2.lookup(ip_address)
    return match.get_info_dict()["country"]["names"]["en"] if match else None
