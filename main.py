import eel
import re
import os
import sys
import json
import shutil
import requests
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)

def download_media(media):
    global PROFILE
    id = str(media["id"])
    source = media["source"]["source"]

    if media["type"] != "photo" and media["type"] != "video":
        return

    ext = re.findall('\.\w+\?', source)
    if len(ext) == 0:
        return
    ext = ext[0][:-1]

    path = "/" + media["type"] + "s/" + id + ext
    file = id + ext
    eel.sendLog(file + "\n")
    r = requests.get(source, stream=True)
    with open("downloads/" + PROFILE + path, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)


def api_request(endpoint, getdata = None, postdata = None):
    global URL
    global API_URL
    global API_HEADER
    global APP_TOKEN
    getparams = {
        "app-token": APP_TOKEN
    }

    if getdata is not None:
        for i in getdata:
            getparams[i] = getdata[i]

    if postdata is None:
        return requests.get(URL + API_URL + endpoint,
                            headers=API_HEADER,
                            params=getparams)
    else:
        return requests.post(URL + API_URL + endpoint + "?app-token=" + APP_TOKEN,
                             headers=API_HEADER,
                             params=getparams,
                             data=postdata)



def get_user_info(profile):
    info = api_request("/users/" + profile).json()
    if "error" in info:
        eel.sendLog("ERROR: " + info["error"]["message"] + "\n")
        exit()
    return info

@eel.expose
def start(username, access_token, user_agent, post_amount):
    global API_HEADER
    global API_HEADER
    global APP_TOKEN
    global PROFILE
    global POST_LIMIT
    USER_AGENT = user_agent
    API_HEADER = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": USER_AGENT,
        "Accept-Encoding": "gzip, deflate"
    }
    PROFILE = username
    API_HEADER["access-token"] = access_token
    POST_LIMIT = post_amount
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.submit(main)

def main():
    global URL
    global API_URL
    global API_HEADER
    global APP_TOKEN
    global PROFILE
    global POST_LIMIT

    URL = "https://onlyfans.com"
    API_URL = "/api2/v2"
    APP_TOKEN = "33d57ade8c02dbc5a333db99ff9ae26a"
    USER_INFO = {}
    PROFILE_INFO = {}
    PROFILE_ID = ""

    eel.sendLog("Getting auth info...\n")

    USER_INFO = get_user_info("customer")
    API_HEADER["user-id"] = str(USER_INFO["id"])
    eel.sendLog("Getting profile info...\n")
    PROFILE_INFO = get_user_info(PROFILE)
    PROFILE_ID = str(PROFILE_INFO["id"])

    if not os.path.isdir("downloads"):
        os.mkdir("downloads")
        eel.sendLog("Created downloads\n")

    if not os.path.isdir("downloads/" + PROFILE):
        os.mkdir("downloads/" + PROFILE)
        eel.sendLog("Created downloads/" + PROFILE + "\n")

    if not os.path.isdir("downloads/" + PROFILE + "/photos"):
        os.mkdir("downloads/" + PROFILE + "/photos")
        eel.sendLog("Created downloads/" + PROFILE + "/photos" + "\n")

    if not os.path.isdir("downloads/" + PROFILE + "/videos"):
        os.mkdir("downloads/" + PROFILE + "/videos")
        eel.sendLog("Created downloads/" + PROFILE + "/videos" + "\n")

    eel.sendLog("Downloading content to downloads/" + PROFILE + "\n\n")
    # get all user posts
    eel.sendLog("Finding posts...\n")
    posts = api_request("/users/" + PROFILE_ID + "/posts", getdata={"limit": POST_LIMIT}).json()

    if len(posts) == 0:
        eel.sendLog("ERROR: 0 posts found.\n")
        exit()

    eel.sendLog("Downloading " + str(len(posts)) + " posts...\n")

    for post in posts:
        if not post["canViewMedia"]:
            continue

        for media in post["media"]:
            executor.submit(download_media, media)

eel.init('web')
eel.start('ofdl.html', size=(700, 321))
