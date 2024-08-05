from flask import Flask
from flask_restful import Api

from resources.rekognition import faceAnalysisResourse, compareResourse

app = Flask(__name__)

api = Api(app)

# 경로와 리소스를 연결한다.
api.add_resource( faceAnalysisResourse , '/face_analysis' )
api.add_resource( compareResourse , '/face_compare' )

if __name__ == '__main__' :
    app.run()
