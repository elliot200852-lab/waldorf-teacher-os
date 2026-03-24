import urllib.request
import urllib.parse
import os
import ssl

context = ssl._create_unverified_context()

def download_audio(text, filename):
    encoded_text = urllib.parse.quote(text)
    url = f"https://tts.edu.tw/tts/tw/api?text={encoded_text}"
    print(f"Downloading {text} to {filename}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context) as response:
            with open(filename, 'wb') as f:
                f.write(response.read())
        print(f"Successfully downloaded {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

output_dir = r"C:\Users\user\waldorf-teacher-os\workspaces\Working_Member\Teacher_林詩閔\niamyio_audio"
os.makedirs(output_dir, exist_ok=True)

download_audio("纏線纏線纏予紧，拋落地下se̍h-lûn-tǹg", os.path.join(output_dir, "kanlok.mp3"))
download_audio("毽子輕輕飛起去，一下踢、兩下盤，大步跳過山", os.path.join(output_dir, "kian_tsi.mp3"))
download_audio("一下抽、一下扯，扯鈴旋甲真大聲", os.path.join(output_dir, "tshe_lin.mp3"))

