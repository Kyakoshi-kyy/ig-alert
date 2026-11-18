import os, re, sys, urllib.request
from curl_cffi import requests

user = os.environ["IG_USER"]
topic = os.environ["NTFY_TOPIC"]

urls = [
    f"https://www.instagram.com/{user}/embed/",
    f"https://imginn.com/{user}/",
]

matches = []
for u in urls:
    try:
        r = requests.get(u, impersonate="chrome", timeout=20)
        print(u, "->", r.status_code)
        if r.status_code == 200:
            found = re.findall(r"/(?:p|reel)/([A-Za-z0-9_-]+)/", r.text)
            if found:
                matches = found
                break
    except Exception as e:
        print("Failed:", u, e)

if not matches:
    print("Blocked or no posts found")
    sys.exit(0)

shortcode = matches[0]
post_url = f"https://www.instagram.com/p/{shortcode}/"

last_id = open("last_id.txt").read().strip() if os.path.exists("last_id.txt") else ""

if shortcode != last_id:
    with open("last_id.txt", "w") as f:
        f.write(shortcode)
    req = urllib.request.Request(
        f"https://ntfy.sh/{topic}",
        data=f"New post on @{user}".encode("utf-8"),
        headers={"Title": f"New post from @{user}", "Click": post_url},
    )
    urllib.request.urlopen(req)
    print("Sent alert for:", shortcode)
else:
    print("No new posts.")
