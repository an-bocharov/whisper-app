import os
import logging
from flask import Flask, render_template, request, jsonify, Response
from werkzeug.utils import secure_filename
import whisper
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Создаем папку для загрузок, если её нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Загружаем модель Whisper при старте приложения
model = whisper.load_model("base")

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def json_response(data, status_code=200):
    return Response(
        json.dumps(data, ensure_ascii=False),
        status=status_code,
        mimetype='application/json'
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        if 'file' not in request.files:
            logger.error("Файл не найден в запросе")
            return json_response({'error': 'Файл не найден'}, 400)
        
        file = request.files['file']
        if file.filename == '':
            logger.error("Имя файла пустое")
            return json_response({'error': 'Файл не выбран'}, 400)
        
        if not allowed_file(file.filename):
            logger.error(f"Неподдерживаемый формат файла: {file.filename}")
            return json_response({'error': 'Неподдерживаемый формат файла'}, 400)
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        logger.info(f"Сохранение файла: {filepath}")
        file.save(filepath)
        
        try:
            logger.info("Начало транскрибации")
            result = model.transcribe(filepath)
            logger.info("Транскрибация завершена")
            
            # Удаляем файл после обработки
            os.remove(filepath)
            logger.info("Временный файл удален")
            
            return json_response({
                'text': result['text'],
                'segments': result['segments']
            })
            
        except Exception as e:
            logger.error(f"Ошибка при транскрибации: {str(e)}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return json_response({'error': str(e)}, 500)
            
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        return json_response({'error': 'Внутренняя ошибка сервера'}, 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001) 