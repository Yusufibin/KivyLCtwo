import requests
from ctypes import *
#g
def calculator(firstname, secondname):


    test=cdll.LoadLibrary("libs/android-v7/strfunc_armeabi-v7a.so")
    test.getName.restype=c_char_p
    test.getValue.restype=c_char_p

    name = test.getName().decode("utf-8")
    value = test.getValue().decode("utf-8")

    
    url = "https://love-calculator.p.rapidapi.com/getPercentage"

    querystring = {"fname": firstname,"sname": secondname}

    headers = {
        'x-rapidapi-host': name,
        'x-rapidapi-key': value
        }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
        jsondata = response.json()
        return jsondata
    except requests.exceptions.HTTPError:
        return "Failed"
    except requests.exceptions.ConnectionError:
        return "Failed"
    except requests.exceptions.Timeout:
        return "Failed"
    except requests.exceptions.RequestException:
        return "Failed"

