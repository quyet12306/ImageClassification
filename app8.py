
from io import BytesIO
from PIL import Image
import requests
url = "https://photo-cms-tpo.epicdn.me/w890/Uploaded/2023/pcgycivo/2016_10_03/1_QGVP.jpg"
# url = "https://api.ipify.org/"
headers = ""
r = requests.get(url=url,headers=headers)

status = r.json
data = r.content
img = Image.open(BytesIO(data))
img.show()
print(f"status = {status}")