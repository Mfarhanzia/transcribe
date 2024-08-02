import whisper
import moviepy.editor as mp


def video_to_audio(video_path=None, audio_path=None):
    video_path = "./video.mp4"
    audio_path = "./audio.wav"
    clip = mp.VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    return True


def get_text_from_audio(audio_path=None, output_path=None):
    if not audio_path:
        audio_path = "./audio.wav"
    if not output_path:
        output_path = "./whisper_transcripted.txt"

    model = whisper.load_model("base")
    
    result = model.transcribe(audio_path)
    with open(output_path, "w") as f:
        f.write(result["text"])


if __name__ == "__main__":
    video_to_audio()
    get_text_from_audio()
