import threading
import time

import numpy as np
import sounddevice as sd
from pynput import keyboard


# サンプル音生成
def generate_sine_wave(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * frequency * t)


# 各楽器の音を定義
kick = generate_sine_wave(100, 0.1)  # バスドラム
snare = generate_sine_wave(300, 0.1)  # スネア
hihat = generate_sine_wave(6000, 0.05)  # ハイハット
metronome = generate_sine_wave(800, 0.05)  # メトロノーム

# リズムパターン（リアルタイムで更新される）
# 16分音符: 1小節16分割
rhythm_pattern = [
    [0] * 16,  # キック
    [0] * 16,  # スネア
    [0] * 16,  # ハイハット
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],  # メトロノーム
]

# 各楽器と対応する音をリスト化
sounds = [kick, snare, hihat, metronome]
keys_to_instruments = {
    "q": 0,
    "w": 1,
    "e": 2,
}  # 'q'でキック, 'w'でスネア, 'e'でハイハット

# BPM設定（1分間の拍数）
bpm = 80
sixteenth_duration = 60 / bpm / 4  # 16分音符の長さ


# 再生用のリズムトラックを作成
def create_rhythm_track(rhythm_pattern, sounds, sixteenth_duration, sample_rate=44100):
    track_length = len(rhythm_pattern[0]) * int(sample_rate * sixteenth_duration)
    track = np.zeros(track_length)

    for instrument_index, pattern in enumerate(rhythm_pattern):
        sound = sounds[instrument_index]
        for beat_index, beat in enumerate(pattern):
            if beat == 1:
                start = beat_index * int(sample_rate * sixteenth_duration)
                end = start + len(sound)
                track[start:end] += sound

    # 音割れを防ぐために正規化
    track = np.clip(track, -1, 1)
    return track


# リズムトラックのループ再生
def play_loop():
    while True:
        track = create_rhythm_track(rhythm_pattern, sounds, sixteenth_duration)
        sd.play(track, samplerate=44100)
        sd.wait()  # 再生終了を待つ


# キーボード入力で音を鳴らしリズムパターンを変更
def on_press(key):
    try:
        if key.char in keys_to_instruments:
            instrument_index = keys_to_instruments[key.char]
            # 即時音を再生
            sd.play(sounds[instrument_index], samplerate=44100)
            sd.wait()  # 再生が終わるまで待つ
            # 次の空いているタイミングにノートを追加
            current_beat = int(
                (time.time() % (len(rhythm_pattern[0]) * sixteenth_duration))
                / sixteenth_duration
            )
            rhythm_pattern[instrument_index][current_beat] = 1
            print(f"追加: 楽器 {instrument_index} -> タイミング {current_beat}")
    except AttributeError:
        pass  # 特殊キーは無視


# キーボード入力を監視するスレッド
def start_keyboard_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


# 並行処理でループ再生とキーボード入力を実行
if __name__ == "__main__":
    print("ループ再生を開始します。キーボード入力でリズムを追加してください:")
    print(" - 'q': キック")
    print(" - 'w': スネア")
    print(" - 'e': ハイハット")
    print("メトロノームはデフォルトで再生されます。")
    threading.Thread(target=play_loop, daemon=True).start()
    start_keyboard_listener()
