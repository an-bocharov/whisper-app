import whisper

def transcribe_audio(audio_path):
    # Загружаем модель (по умолчанию используется модель "base")
    model = whisper.load_model("base")
    
    # Транскрибируем аудио
    result = model.transcribe(audio_path)
    
    # Выводим результат
    print("Текст:", result["text"])
    
    # Если нужны временные метки для каждого сегмента
    print("\nСегменты с временными метками:")
    for segment in result["segments"]:
        print(f"[{segment['start']:.1f}s -> {segment['end']:.1f}s] {segment['text']}")

if __name__ == "__main__":
    # Замените "audio.mp3" на путь к вашему аудиофайлу
    audio_file = "audio.mp3"
    transcribe_audio(audio_file) 