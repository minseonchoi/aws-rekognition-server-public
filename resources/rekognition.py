
from datetime import datetime
from flask_restful import Resource
from flask import request

import boto3

from config import Config

from PIL import Image, ImageDraw, ImageFont
import io
import os



class faceAnalysisResourse(Resource):
    
    def post(self) :

        if 'photo' not in request.files :
            return {"result":"fail", "error":"사진은 필수 입니다"}, 400
        
        file = request.files['photo']

        current_time = datetime.now()
        file_name = current_time.isoformat().replace(':','')+'.jpg'

        file.name = file_name

        client = boto3.client('s3',
                              aws_access_key_id = Config.AWS_ACCESS_KEY,
                              aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY)
        
        try :
            client.upload_fileobj(file,
                                    Config.S3_BUCKET,
                                    file_name,
                                    ExtraArgs = {'ACL' : 'public-read',
                                               'ContentType':'image/jpeg'})
        except Exception as e :
            return {"result":"fail", "error":str(e)}, 500
        
        faceAnalysis = self.detect_faces(file.name, Config.S3_BUCKET)

        print(faceAnalysis)

        return {"result":"success", "lables": faceAnalysis}



    def detect_faces(self, photo, bucket):
        
        client = boto3.client('rekognition', 
                                region_name='ap-northeast-2',
                                aws_access_key_id = Config.AWS_ACCESS_KEY,
                              aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY)

        response = client.detect_faces(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
                                    Attributes=['ALL'])

        print('PhotoId : ' + photo)
        print(response['FaceDetails'])

        faceAnalysis = []
        for faceDetail in response['FaceDetails']:
            # Access predictions for individual face details and print them
            print("나이: " + str(faceDetail['AgeRange']['Low']) + " ~ " + str(faceDetail['AgeRange']['High']))
            print("성별: " + str(list(faceDetail['Gender'].values())[0]) + ", 정확도 : " + str(list(faceDetail['Gender'].values())[1]))
            print("스마일: " + str(list(faceDetail['Smile'].values())[0]) + ", 정확도 : " + str(list(faceDetail['Smile'].values())[1]))
            print("안경: " + str(list(faceDetail['Eyeglasses'].values())[0]) + ", 정확도 : " + str(list(faceDetail['Eyeglasses'].values())[1]))
            print("얼굴 보임 유무: " + str(list(faceDetail['FaceOccluded'].values())[0]) + ", 정확도 : " + str(list(faceDetail['FaceOccluded'].values())[1]))
            print("기분: " + str(faceDetail['Emotions'][0]['Type']) + ", 정확도 : " +  str(faceDetail['Emotions'][0]['Confidence']))

        


            detail = {'AgeLow':faceDetail['AgeRange']['Low'],
                      'AgeHigh':faceDetail['AgeRange']['High'],
                      'Gender':faceDetail['Gender'],
                      'Smile':faceDetail['Smile'],
                      'Eyeglasses':faceDetail['Eyeglasses'],
                      'FaceOccluded':faceDetail['FaceOccluded'],
                      'Emotions':faceDetail['Emotions'][0]
                      }

            # faceAnalysis.append()
            faceAnalysis.append(detail)

        return faceAnalysis

class compareResourse(Resource):
    
    def post(self):
        if 'photo1' not in request.files or 'photo2' not in request.files:
            return {'result': 'fail', 'error': '사진은 필수입니다.'}, 400
        
        sourceFile = request.files['photo1']
        targetFile = request.files['photo2']

        if 'image' not in sourceFile.content_type or 'image' not in targetFile.content_type:
            return {'result': 'fail', 'error': '이미지 파일만 업로드 가능합니다.'}, 400
        
        current_time = datetime.now()
        fileName1 = current_time.isoformat().replace(':', '') + '.jpg'
        fileName2 = current_time.isoformat().replace(':', '') + '_2.jpg'
        
        sourceFile.name = fileName1
        targetFile.name = fileName2

        # S3에 이미지 파일 업로드
        client = boto3.client('s3',
                              aws_access_key_id=Config.AWS_ACCESS_KEY,
                              aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY)
        
        try:
            client.upload_fileobj(sourceFile,
                                  Config.S3_BUCKET,
                                  fileName1,
                                  ExtraArgs={'ACL': 'public-read',
                                             'ContentType': 'image/jpeg'})
            
            client.upload_fileobj(targetFile,
                                  Config.S3_BUCKET,
                                  fileName2,
                                  ExtraArgs={'ACL': 'public-read',
                                             'ContentType': 'image/jpeg'})
            
        except Exception as e:
            return {'result': 'fail', 'error': str(e)}, 500

        # 얼굴 비교 수행
        num_matches, similarity_percent, face_details = self.compare_faces(fileName1, fileName2, Config.S3_BUCKET)
        
        # 얼굴 위치를 이미지에 표시
        self.draw_bounding_boxes(fileName2, face_details, Config.S3_BUCKET)
        
        return {'result': 'success', 'face_matches': num_matches, 'similarity_percent': f"{similarity_percent:.2f}"}
    
    def compare_faces(self, sourceFile, targetFile, bucket):
        session = boto3.Session(
            aws_access_key_id=Config.AWS_ACCESS_KEY,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
        )
        client = session.client('rekognition', region_name='ap-northeast-2')

        response = client.compare_faces(
            SimilarityThreshold=80,
            SourceImage={'S3Object': {'Bucket': bucket, 'Name': sourceFile}},
            TargetImage={'S3Object': {'Bucket': bucket, 'Name': targetFile}}
        )

        face_details = response['FaceMatches']
        for faceMatch in face_details:
            position = faceMatch['Face']['BoundingBox']
            similarity = str(faceMatch['Similarity'])
            print('The face at ' +
                  str(position['Left']) + ' ' +
                  str(position['Top']) +
                  ' matches with ' + similarity + '% confidence')

        return len(face_details), face_details[0]['Similarity'] if face_details else 0, face_details

    def draw_bounding_boxes(self, image_file, face_details, bucket):
        # S3에서 이미지를 다운로드합니다.
        s3 = boto3.client('s3',
                          aws_access_key_id=Config.AWS_ACCESS_KEY,
                          aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY)
        
        image_object = s3.get_object(Bucket=bucket, Key=image_file)
        image_content = image_object['Body'].read()
        
        image = Image.open(io.BytesIO(image_content))
        img_width, img_height = image.size
        draw = ImageDraw.Draw(image)

        # Windows에서 사용할 글꼴 설정
        font_path = "C:/Windows/Fonts/arial.ttf"
        font_size = 20  # 글꼴 크기 설정
        font = ImageFont.truetype(font_path, font_size)
        
        for face in face_details:
            box = face['Face']['BoundingBox']
            left = img_width * box['Left']
            top = img_height * box['Top']
            width = img_width * box['Width']
            height = img_height * box['Height']
            similarity = face['Similarity']
            
            points = (
                (left, top),
                (left + width, top),
                (left + width, top + height),
                (left, top + height),
                (left, top)
            )
            
            # 유사도 퍼센트 추가 (먼저 박스를 그린 후 텍스트를 그림)
            draw.line(points, fill='red', width=5)
            text_position = (left, top - 30)
            draw.text(text_position, f"{similarity:.2f}%", fill='red', font=font)
        
        # 또는 S3에 다시 업로드
        buffer = io.BytesIO()
        image.save(buffer, 'JPEG')
        buffer.seek(0)
        s3.put_object(Bucket=bucket, Key=f"annotated_{image_file}", Body=buffer, ContentType='image/jpeg', ACL='public-read')

        return image