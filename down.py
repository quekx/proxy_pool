from flask import Flask
from flask import send_file

app = Flask(__name__)

@app.route('/download')
def download_file():
    return send_file('test.json', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)