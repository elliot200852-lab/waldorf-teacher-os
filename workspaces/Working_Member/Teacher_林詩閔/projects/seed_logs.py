import re
import os

profile_path = r"workspaces\Working_Member\Teacher_林詩閔\projects\class-4c\taiwanese\di-profile.yaml"
log_dir = r"workspaces\Working_Member\Teacher_林詩閔\projects\class-4c\records\student-logs"

with open(profile_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

current_student = {}
for line in lines:
    if " - { id: " in line:
        match = re.search(r'id: ([\w\-]+), name: ([\u4e00-\u9fa5]+).*note: "(.*)"', line)
        if match:
            sid = match.group(1)
            name = match.group(2)
            note = match.group(3)
            
            file_path = os.path.join(log_dir, f"{name}.md")
            content = f"# {name} ({sid}) - 學習紀錄\n\n[Source: 台語科-初始評量] (2026-03-23)\n{note}\n\n---\n"
            with open(file_path, "w", encoding="utf-8") as out:
                out.write(content)
print("Logs created!")
