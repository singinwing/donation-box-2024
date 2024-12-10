import numpy as np
import sounddevice as sd


# サンプル音生成 (1秒間に44100サンプル)
def generate_sine_wave(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * frequency * t)


# 各楽器の音を定義
kick = generate_sine_wave(100, 0.1)  # バスドラム
snare = generate_sine_wave(300, 0.1)  # スネア
hihat = generate_sine_wave(6000, 0.05)  # ハイハット

# リズムパターン（1: 再生, 0: 無音）
# 各行が楽器のパターンを表す
rhythm_pattern = [
    [1, 0, 0, 0, 1, 0, 0, 0],  # キック
    [0, 0, 1, 0, 0, 0, 1, 0],  # スネア
    [1, 1, 1, 1, 1, 1, 1, 1],  # ハイハット
]

# 各楽器と対応する音をリスト化
sounds = [kick, snare, hihat]

# BPM設定（1分間の拍数）
bpm = 120
beat_duration = 60 / bpm  # 1拍の長さ


# 再生用のリズムトラックを作成
def create_rhythm_track(rhythm_pattern, sounds, beat_duration, sample_rate=44100):
    track_length = len(rhythm_pattern[0]) * int(sample_rate * beat_duration)
    track = np.zeros(track_length)

    for instrument_index, pattern in enumerate(rhythm_pattern):
        sound = sounds[instrument_index]
        for beat_index, beat in enumerate(pattern):
            if beat == 1:
                start = beat_index * int(sample_rate * beat_duration)
                end = start + len(sound)
                track[start:end] += sound

    # 音割れを防ぐために正規化
    track = np.clip(track, -1, 1)
    return track


# トラックを生成して再生
track = create_rhythm_track(rhythm_pattern, sounds, beat_duration)
print("再生中...")
sd.play(track, samplerate=44100)
sd.wait()
print("再生終了")
