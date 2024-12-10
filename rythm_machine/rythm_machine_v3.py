import numpy as np
import sounddevice as sd
import soundfile as sf


# WAV ファイルを読み込む関数
def load_wav(file_path):
    data, samplerate = sf.read(file_path)

    # ステレオ音声をモノラルに変換
    if len(data.shape) > 1 and data.shape[1] == 2:  # ステレオかどうか確認
        data = np.mean(data, axis=1)  # 2チャンネルを平均してモノラルに変換

    return data, samplerate


# リズムパターン（1: 再生, 0: 無音）
# 各行が楽器のパターンを表す
rhythm_pattern = [
    [1, 0, 0, 0, 1, 0, 0, 0],  # キック
    [0, 0, 1, 0, 0, 0, 1, 0],  # スネア
    [1, 1, 1, 1, 1, 1, 1, 1],  # ハイハット
]

# WAV ファイルを指定
kick_file = "kick.wav"  # キックドラムの音
snare_file = "snare.wav"  # スネアドラムの音
hihat_file = "hihat.wav"  # ハイハットの音

# WAV ファイルをロード
kick, samplerate = load_wav(kick_file)
snare, _ = load_wav(snare_file)  # サンプルレートはすべて同じ前提
hihat, _ = load_wav(hihat_file)

# 各楽器の音をリスト化
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
                track[start:end] += sound[: end - start]  # 必要ならトリミング

    # 音割れを防ぐために正規化
    track = np.clip(track, -1, 1)
    return track


# トラックを生成して再生
track = create_rhythm_track(rhythm_pattern, sounds, beat_duration, samplerate)
print("再生中...")
sd.play(track, samplerate=samplerate)
sd.wait()
print("再生終了")
