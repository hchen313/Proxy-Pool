import requests
from bs4 import BeautifulSoup
import telnetlib
import pandas as pd
import lxml
import os.path as path
from multiprocessing import Pool



def check_connection(row):
    dict = row
    tn = None
    for _ in range(100):
        try:
            tn = telnetlib.Telnet(dict["IP Address"], dict["Port"], timeout=1)
            dict["Score"] = 100
        except:
            dict["Score"] -= 1
            if dict["Score"] == 0:
                return None
        finally:
            if tn:
                tn.close()
    return dict

if __name__ == '__main__':
    if path.exists("proxies.csv"):
        db = pd.read_csv("proxies.csv")
    else:
        colns = ["IP Address", "Port", "Code", "Country", "Anonymity", "Google", "Https", "Last Checked", "Score"]
        db = pd.DataFrame(columns=colns)

    url = "https://free-proxy-list.net/"
    head = {
        "User-Agent": ""
    }

    response = requests.get(url=url, headers=head)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="table table-striped table-bordered")
    df_db = pd.read_html(str(table))[0] if table is not None else None
    df = db
    if df_db is not None:
        df_db["Score"] = 10
        df = pd.concat([df_db.reset_index(drop=True), db.reset_index(drop=True)], ignore_index=True)
        df = df.drop_duplicates("IP Address")

    lst = list(df.to_dict(orient='records'))
    with Pool() as pool:
        res = pool.map(check_connection, lst)
    filtered_list = [item for item in res if item is not None]
    df = pd.DataFrame(filtered_list)
    f = open("proxies.csv", "w")
    f.truncate()
    f.close()
    df.to_csv("proxies.csv", index=False)