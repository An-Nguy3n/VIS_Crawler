import os

def get_manifest_json(id):
    return """{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Proxy_%s",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
""" % str(id)


def get_background_js(host, port, username, password):
    return """var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (host, port, username, password)


def create_proxy_folders():
    with open("proxies.txt", "r") as f:
        proxies = f.read().split("\n")

    for i in range(len(proxies)):
        os.makedirs(f"Proxies/Proxy_{i}", exist_ok=True)
        host, port, username, password = proxies[i].split(":")
        manifest_json = get_manifest_json(i)
        background_js = get_background_js(host, port, username, password)
        with open(f"Proxies/Proxy_{i}/manifest.json", "w") as f:
            f.write(manifest_json)

        with open(f"Proxies/Proxy_{i}/background.js", "w") as f:
            f.write(background_js)


import undetected_chromedriver as uc
import numpy as np
from bs4 import BeautifulSoup
import time
import random


class Browser:
    def __init__(self, use_proxy=True, proxy_id=None):
        if proxy_id is None:
            random_proxy = True
        else:
            random_proxy = False

        self.use_proxy = use_proxy
        self.proxy_id = proxy_id
        self.random_proxy = random_proxy
        self.reset_browser()

    def reset_browser(self):
        try:
            self.driver.close()
            self.driver.quit()
            print("Reseted")
        except:
            pass

        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")

        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.geolocation": 2
        }
        options.add_experimental_option("prefs", prefs)

        if self.use_proxy:
            if self.random_proxy:
                self.proxy_id = np.random.randint(250)
            else:
                pass

            options.add_argument(f"--load-extension=/Users/annnguy3n/Desktop/VIS_Crawler/Proxies/Proxy_{self.proxy_id}")

        print(self.proxy_id)
        self.driver = uc.Chrome(options=options)
        self.driver.get("https://httpbin.org/ip")

    def get_soup(self):
        return BeautifulSoup(self.driver.page_source, "html.parser")

    def scroll_to_bottom(self, wait_page_load=1):
        current_height = self.driver.execute_script("return document.body.scrollHeight;")
        while True:
            self.driver.execute_script(f"window.scrollTo(0, {current_height});")
            time.sleep(wait_page_load)
            new_height = self.driver.execute_script("return document.body.scrollHeight;")
            if new_height == current_height: break

            current_height = new_height
