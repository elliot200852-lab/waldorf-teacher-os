import urllib.request
import json
import ssl

def query_moedict_taigi(word):
    """
    使用萌典 API 查詢台語詞彙的發音與解釋（使用內建 urllib 以確保相容性）。
    """
    # 萌典台語區塊的 API endpoint (需要對中文進行引波)
    encoded_word = urllib.parse.quote(word)
    url = f"https://www.moedict.tw/t/{encoded_word}.json"
    
    # 忽略 SSL 憑證檢查 (避免某些環境下的問題)
    context = ssl._create_unverified_context()
    
    try:
        with urllib.request.urlopen(url, context=context) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            print(f"=== 詞條：{data.get('t', word)} ===")
            
            # 遍歷不同的讀音與解釋
            for h in data.get('h', []):
                # 台語通常在 'T' 欄位有台羅或 POJ
                reading = h.get('T', '無標註讀音')
                print(f"讀音：{reading}")
                
                # 取得音檔 ID
                audio_id = h.get('audio_id')
                if audio_id:
                    audio_url = f"https://www.moedict.tw/t/{audio_id}.mp3"
                    print(f"音檔連結：{audio_url}")
                
                # 解釋部分
                for def_item in h.get('d', []):
                    # f 是定義, e 是範例
                    definition = def_item.get('f', '')
                    example = def_item.get('e', [])
                    print(f"▶ 解釋：{definition}")
                    if example:
                        # 處理範例中的字詞，萌典範例通常是 list
                        print(f"  例句：{', '.join(example)}")
                        
    except Exception as e:
        print(f"查詢「{word}」失敗：此詞彙可能不在萌典台語區塊中。({e})")

if __name__ == "__main__":
    # 測試查詢「月娘」與「水果」
    test_words = ["月娘", "水果"]
    for w in test_words:
        query_moedict_taigi(w)
        print("-" * 30)
