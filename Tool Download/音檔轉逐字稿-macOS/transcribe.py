#!/usr/bin/env python3
"""
音檔轉逐字稿工具（含說話者辨識）
使用 mlx-whisper（Apple Silicon 優化）進行語音轉文字，
搭配 pyannote-audio 進行說話者辨識（Speaker Diarization）。

支援格式：m4a, mp3, wav, flac, ogg, wma, aac
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

SUPPORTED_FORMATS = {".m4a", ".mp3", ".wav", ".flac", ".ogg", ".wma", ".aac"}

# 預設使用 large-v3 turbo，中文辨識效果好且速度快
DEFAULT_MODEL = "mlx-community/whisper-large-v3-turbo"


def load_env(script_dir: str):
    """從 .env 檔載入環境變數"""
    env_path = Path(script_dir) / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def format_timestamp(seconds: float) -> str:
    """將秒數轉換為 HH:MM:SS 格式"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def transcribe_file(audio_path: str, model_name: str = DEFAULT_MODEL) -> dict:
    """轉錄單一音檔，回傳結果字典"""
    import mlx_whisper

    print(f"\n  [1/2] 正在進行語音轉文字...")
    print(f"  模型: {model_name}")
    print(f"  （首次使用會下載模型，請稍候...）\n")

    start_time = time.time()

    result = mlx_whisper.transcribe(
        audio_path,
        path_or_hf_repo=model_name,
        language="zh",
        verbose=False,
    )

    elapsed = time.time() - start_time
    print(f"  語音轉文字完成，耗時 {elapsed:.1f} 秒")

    return result


def diarize_audio(audio_path: str) -> list:
    """
    使用 pyannote-audio 進行說話者辨識。
    回傳列表，每個元素為 (start, end, speaker_label)。
    如果無法辨識（缺少 token 或模型），回傳空列表。
    """
    hf_token = os.environ.get("HF_TOKEN", "").strip()
    if not hf_token:
        print("  [提示] 未設定 HF_TOKEN，跳過說話者辨識。")
        print("  （在 .env 檔中設定 HF_TOKEN 即可啟用）")
        return []

    try:
        from pyannote.audio import Pipeline
    except ImportError:
        print("  [提示] 尚未安裝 pyannote-audio，跳過說話者辨識。")
        print("  （執行 setup.sh 安裝相依套件即可啟用）")
        return []

    print(f"\n  [2/2] 正在進行說話者辨識...")
    print(f"  （首次使用會下載辨識模型，請稍候...）\n")

    start_time = time.time()

    try:
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=hf_token,
        )

        # 如果有 MPS（Apple Silicon GPU），使用它加速
        import torch
        if torch.backends.mps.is_available():
            import torch
            pipeline.to(torch.device("mps"))
            print("  使用 Apple Silicon GPU 加速")

        diarization = pipeline(audio_path)

        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append((turn.start, turn.end, speaker))

        elapsed = time.time() - start_time
        # 統計說話者數量
        speakers = set(s[2] for s in segments)
        print(f"  說話者辨識完成，耗時 {elapsed:.1f} 秒")
        print(f"  偵測到 {len(speakers)} 位說話者")

        return segments

    except Exception as e:
        print(f"  [警告] 說話者辨識失敗: {e}")
        print("  將以無說話者標記模式繼續輸出。")
        return []


def assign_speakers(whisper_segments: list, diarization_segments: list) -> list:
    """
    將 whisper 的文字片段與 pyannote 的說話者辨識結果對齊。
    使用「重疊比例最高」的方式決定每個文字片段的說話者。

    回傳列表，每個元素為 dict:
        {"start": float, "end": float, "text": str, "speaker": str}
    """
    if not diarization_segments:
        # 沒有辨識結果，回傳不帶 speaker 的原始段落
        return [
            {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
                "speaker": None,
            }
            for seg in whisper_segments
            if seg["text"].strip()
        ]

    result = []
    for seg in whisper_segments:
        text = seg["text"].strip()
        if not text:
            continue

        seg_start = seg["start"]
        seg_end = seg["end"]
        seg_duration = seg_end - seg_start

        if seg_duration <= 0:
            result.append({
                "start": seg_start, "end": seg_end,
                "text": text, "speaker": None,
            })
            continue

        # 計算每個說話者與此段的重疊時間
        speaker_overlap = {}
        for d_start, d_end, d_speaker in diarization_segments:
            overlap_start = max(seg_start, d_start)
            overlap_end = min(seg_end, d_end)
            overlap = max(0, overlap_end - overlap_start)
            if overlap > 0:
                speaker_overlap[d_speaker] = speaker_overlap.get(d_speaker, 0) + overlap

        # 選擇重疊最多的說話者
        if speaker_overlap:
            best_speaker = max(speaker_overlap, key=speaker_overlap.get)
        else:
            best_speaker = None

        result.append({
            "start": seg_start, "end": seg_end,
            "text": text, "speaker": best_speaker,
        })

    return result


def merge_speaker_segments(segments: list) -> list:
    """
    合併連續同一說話者的段落為完整語段，提升可讀性。
    回傳列表，每個元素為 dict:
        {"start": float, "end": float, "text": str, "speaker": str}
    """
    if not segments:
        return []

    merged = []
    current = {
        "start": segments[0]["start"],
        "end": segments[0]["end"],
        "text": segments[0]["text"],
        "speaker": segments[0]["speaker"],
    }

    for seg in segments[1:]:
        if seg["speaker"] == current["speaker"] and seg["speaker"] is not None:
            # 同一說話者，合併
            current["end"] = seg["end"]
            current["text"] += seg["text"]
        else:
            merged.append(current)
            current = {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"],
                "speaker": seg["speaker"],
            }

    merged.append(current)
    return merged


def create_speaker_map(segments: list) -> dict:
    """
    為 pyannote 的說話者標籤建立友善的中文名稱對應。
    例如 SPEAKER_00 -> 說話者 A, SPEAKER_01 -> 說話者 B
    """
    speakers = []
    seen = set()
    for seg in segments:
        sp = seg.get("speaker")
        if sp and sp not in seen:
            speakers.append(sp)
            seen.add(sp)

    labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    speaker_map = {}
    for i, sp in enumerate(speakers):
        if i < len(labels):
            speaker_map[sp] = f"說話者 {labels[i]}"
        else:
            speaker_map[sp] = f"說話者 {i+1}"

    return speaker_map


def result_to_markdown(
    whisper_result: dict,
    audio_path: str,
    diarization_segments: list = None,
) -> str:
    """將 whisper 結果（搭配說話者辨識）轉換為 Markdown 格式"""
    filename = Path(audio_path).stem
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    whisper_segs = whisper_result.get("segments", [])
    has_diarization = bool(diarization_segments)

    lines = []
    lines.append(f"# {filename}\n")
    lines.append(f"- 來源檔案: `{Path(audio_path).name}`")
    lines.append(f"- 轉錄時間: {now}")
    lines.append(f"- 語言: {whisper_result.get('language', '未知')}")
    lines.append(f"- 說話者辨識: {'已啟用' if has_diarization else '未啟用'}")

    if has_diarization:
        # 對齊並合併說話者段落
        aligned = assign_speakers(whisper_segs, diarization_segments)
        merged = merge_speaker_segments(aligned)
        speaker_map = create_speaker_map(merged)

        num_speakers = len(speaker_map)
        lines.append(f"- 偵測說話者數: {num_speakers} 人")

        # 說話者對照表
        if speaker_map:
            names = ", ".join(
                f"{v}（{k}）" for k, v in speaker_map.items()
            )
            lines.append(f"- 說話者代號: {names}")

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 逐字稿（含說話者標記）\n")

        current_speaker = None
        for seg in merged:
            ts = format_timestamp(seg["start"])
            speaker = seg.get("speaker")
            speaker_name = speaker_map.get(speaker, "未知") if speaker else "未知"
            text = seg["text"]

            if speaker != current_speaker:
                # 說話者切換時加上標題
                if current_speaker is not None:
                    lines.append("")  # 段落間空行
                lines.append(f"### {speaker_name} **[{ts}]**\n")
                current_speaker = speaker

            lines.append(f"{text}\n")

    else:
        # 無說話者辨識的原始格式
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 逐字稿\n")

        if not whisper_segs:
            lines.append(whisper_result.get("text", "（無內容）"))
        else:
            for seg in whisper_segs:
                ts = format_timestamp(seg["start"])
                text = seg["text"].strip()
                if text:
                    lines.append(f"**[{ts}]** {text}\n")

    # 全文區塊
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 全文\n")

    if has_diarization:
        aligned = assign_speakers(whisper_segs, diarization_segments)
        merged = merge_speaker_segments(aligned)
        speaker_map = create_speaker_map(merged)

        current_speaker = None
        for seg in merged:
            speaker = seg.get("speaker")
            speaker_name = speaker_map.get(speaker, "未知") if speaker else "未知"
            text = seg["text"]

            if speaker != current_speaker:
                if current_speaker is not None:
                    lines.append("")
                lines.append(f"**{speaker_name}：**")
                current_speaker = speaker

            lines.append(f"{text}")
    else:
        full_text = whisper_result.get("text", "").strip()
        lines.append(full_text if full_text else "（無內容）")

    lines.append("")
    return "\n".join(lines)


def process_file(audio_path: str, model_name: str = DEFAULT_MODEL):
    """處理單一檔案：轉錄 + 說話者辨識 → Markdown"""
    path = Path(audio_path)

    if not path.exists():
        print(f"  [錯誤] 找不到檔案: {audio_path}")
        return

    if path.suffix.lower() not in SUPPORTED_FORMATS:
        print(f"  [跳過] 不支援的格式: {path.suffix} ({path.name})")
        return

    print(f"\n{'='*60}")
    print(f"  處理中: {path.name}")
    print(f"{'='*60}")

    # Step 1: 語音轉文字
    whisper_result = transcribe_file(str(path), model_name)

    # Step 2: 說話者辨識
    diarization_segments = diarize_audio(str(path))

    # Step 3: 合併輸出
    markdown = result_to_markdown(whisper_result, str(path), diarization_segments)

    output_path = path.with_suffix(".md")
    output_path.write_text(markdown, encoding="utf-8")

    print(f"\n  已輸出: {output_path.name}")
    if diarization_segments:
        speakers = set(s[2] for s in diarization_segments)
        print(f"  （含 {len(speakers)} 位說話者標記）")
    return str(output_path)


def main():
    if len(sys.argv) < 2:
        print("""
  音檔轉逐字稿工具（含說話者辨識）
  ====================================

  用法:
    ./transcribe.sh <音檔路徑> [音檔路徑2] ...

  支援格式: m4a, mp3, wav, flac, ogg, wma, aac

  功能:
    - 語音轉文字（mlx-whisper）
    - 說話者辨識（pyannote-audio，需設定 HF_TOKEN）

  範例:
    ./transcribe.sh recording.m4a
    ./transcribe.sh *.mp3

  設定:
    在 .env 檔中設定 HF_TOKEN 以啟用說話者辨識。
    執行 setup.sh 安裝必要套件。
        """)
        sys.exit(1)

    # 載入 .env
    script_dir = Path(__file__).resolve().parent
    load_env(str(script_dir))

    files = sys.argv[1:]
    model = os.environ.get("WHISPER_MODEL", DEFAULT_MODEL)

    print(f"\n  準備轉錄 {len(files)} 個檔案...")
    print(f"  使用模型: {model}")
    hf_token = os.environ.get("HF_TOKEN", "").strip()
    if hf_token:
        print(f"  說話者辨識: 已啟用")
    else:
        print(f"  說話者辨識: 未啟用（缺少 HF_TOKEN）")

    outputs = []
    for f in files:
        result = process_file(f, model)
        if result:
            outputs.append(result)

    print(f"\n{'='*60}")
    print(f"  全部完成！共轉錄 {len(outputs)} 個檔案:")
    for o in outputs:
        print(f"    -> {o}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
