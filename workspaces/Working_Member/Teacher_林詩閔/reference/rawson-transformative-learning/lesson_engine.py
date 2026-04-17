import os
import json
from datetime import datetime

# 這是「轉化性學習教學方法」的核心提示字典
# 在每一個設計步驟中，腳本會自動提示相關的教育學理據與方法
METHODS_GUIDELINES = {
    "Developmental tasks": "檢核：目前的內容是否符合該年齡層兒童的發展任務？（例如：9歲跨越盧比肯河、14歲青春期思考重組）",
    "Pedagogical reasoning": "檢核：為什麼選擇這個內容？是否有意識地透過這份素材在幫助學生的身、心、靈發展，而不是單純傳授知識？",
    "Warm up activities": "提示：這是『準備 (Attuning)』階段。請設計朗誦、節奏拍打或肢體活動，幫助學生進入平靜且警覺的學習狀態。",
    "Method of recall": "檢核：回顧不應只是老師問學生答。提示：請嘗試使用多元方式：如快速素描、配對分享或戲劇定格 (Freeze framing)。",
    "New content": "提示：這是『沉浸 (Immersion)』階段。請盡量產出「具體素材」（如設計好的對話、特定的唸謠、遊戲規則或故事腳本）。若為專科課，請注意與主課程的呼應。",
    "Transitions between activities": "檢核：活動的轉換是否流暢？是否有考量到課堂的「呼與吸」（集中與放鬆）之節奏交替？",
    "Assignments": "提示：這是『鞏固 (Consolidating)』與『應用 (Applying)』。請著重於主課程工作本 (Main lesson books) 的編輯與反思，而非傳統抄寫。",
    "Teaching Self-Evaluation": "檢核：課後反思。語言吸收是否自然？圖像設計是否能跨科共鳴？身心節奏（呼與吸）是否順暢引導學生？"
}

# 課堂設計與自我評鑑表的框架
LESSON_TEMPLATE = [
    ("發展任務 (Developmental tasks)", True),
    ("主題課程目標 (Aims for the block)", False),
    ("課堂教學目標 (Aims for the lesson)", False),
    ("主題課程內容 (Content for the block)", False),
    ("教育學理據 (Pedagogical reasoning)", True),
    ("主要課程資源 / 文獻 (Main curriculum sources)", False),
    ("課程規劃與時間分配 - 單堂或多堂 (Lesson outlines and timeframe)", False),
    ("課堂開始 / 問候 (Start of lesson/greeting)", False),
    ("暖身活動 (Warm up activities)", True),
    ("回顧的方法 (Method of recall)", True),
    ("活動間的轉場 (Transitions between activities)", True),
    ("新授內容與具體教學素材 (New content & Concrete materials)", True),
    ("作業設計-課堂內外 (Assignments)", True),
    ("課堂結束 (End of the lesson)", False),
    ("教學自我評鑑 (Teaching Self-Evaluation)", False),
]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("=" * 60)
    print(" 華德福 Lesson Engine: 課堂設計與自我評鑑工作流 ".center(50))
    print("=" * 60)
    print(">> 系統已載入「轉化性學習教學方法」與「課堂設計表」<<")
    print("我們即將開始一步步進行教案設計，並在重要步驟進行強制檢核。\n")
    
    lesson_name = input("請輸入本次課程名稱或主題：")
    
    lesson_data = {}
    
    for step_name, requires_verification in LESSON_TEMPLATE:
        print("\n" + "-" * 60)
        print(f"📌 目前步驟：{step_name}")
        
        # 如果該步驟有對應的教學方法提示，則顯示出來
        for key in METHODS_GUIDELINES:
            if key in step_name:
                print(f"💡 【系統提示與檢核標準】\n{METHODS_GUIDELINES[key]}")
        
        # 讓使用者輸入設計內容
        print("-" * 60)
        user_input = input("👉 請輸入你的設計內容 (多行請直接連續輸入，按 Enter 結束本段落)：\n")
        
        # 若該步驟需要檢核
        if requires_verification:
            while True:
                confirm = input("\n⚠️ 【自我評鑑檢核】：請問你確認這個設計符合上方的轉化性學習準則嗎？ (y/n): ")
                if confirm.lower() == 'y':
                    break
                else:
                    print("🔄 請重新思考並修改您的設計：")
                    user_input = input("👉 請輸入修改後的設計內容：\n")
        
        lesson_data[step_name] = user_input

    # 提供教師增修與自訂欄位
    while True:
        print("\n" + "=" * 60)
        print("【教案初稿完成】您可以在此階段「檢視與修改既有欄位」或「新增自訂欄位」。")
        print("1. 檢視與修改既有欄位")
        print("2. 新增自訂欄位")
        print("3. 完成教案，準備輸出")
        choice = input("👉 請選擇操作 (1/2/3): ")
        
        if choice == '1':
            options = list(lesson_data.keys())
            for idx, key in enumerate(options):
                print(f"{idx+1}. {key}")
            edit_idx = input("👉 請輸入要修改的欄位編號 (按 Enter 取消): ")
            if edit_idx.isdigit() and 1 <= int(edit_idx) <= len(options):
                target_key = options[int(edit_idx)-1]
                print(f"\n[目前 {target_key} 的內容]：\n{lesson_data[target_key]}")
                new_content = input("👉 請輸入新的內容 (若不修改請直接按 Enter)：\n")
                if new_content.strip():
                    lesson_data[target_key] = new_content
                    print(f"✅ {target_key} 已更新！")
            else:
                print("已取消修改或輸入無效。")

        elif choice == '2':
            new_field = input("👉 請輸入新增欄位名稱 (例如：特別輔導計畫，按 Enter 取消): ")
            if new_field.strip():
                new_content = input(f"👉 請輸入「{new_field}」的設計內容：\n")
                lesson_data[new_field] = new_content
                print(f"✅ 新欄位「{new_field}」已加入！")
            else:
                print("已取消新增。")

        elif choice == '3':
            break
        else:
            print("請輸入有效的選項。")

    # 輸出教案結果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"LessonPlan_{lesson_name}_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# 華德福教案設計：{lesson_name}\n\n")
        f.write(f"*建立時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        for step, content in lesson_data.items():
            f.write(f"### {step}\n{content}\n\n")
            
    print("\n" + "=" * 60)
    print(f"✅ 教案設計完成！已成功輸出至：{filename}")
    print("=" * 60)

if __name__ == "__main__":
    main()
