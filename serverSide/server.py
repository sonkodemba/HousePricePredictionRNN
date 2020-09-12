import json
import requests
import pandas as pd
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=True, help="path of test csv file")

args = vars(ap.parse_args())
path = args["path"]


# setting header to send and accept responses
def serverFile(address):
    # Setting the headers format to be sent to be sent and accept json responses
    header = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    # load csv data
    df = pd.read_csv(path, encoding="utf-8-sig")
    # Convert the data file to json format
    # post data to server
    resp = requests.post(address, data=df.to_json(orient='records'), headers=header)
    if resp.status_code == 200:
        # get response as SalePrice
        resp.json()


if __name__ == '__main__':
    serverFile('http://127.0.0.1:5000/predict')
