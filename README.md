<img src="https://capsule-render.vercel.app/api?type=rounded&color=848484&height=150&section=header&text=AWS_REKOGNITION&fontColor=fff&animation=fadeIn&fontSize=50&stroke=000&strokeWidth=2" />

# AWS Rekognition을 이용한 얼굴 분석 / 비교
### 인공지능을 활용한 사람 얼굴 분석 및 다른 사진으로 얼굴 비교하는 Restful API 개발

[프로젝트 기술서](https://docs.google.com/presentation/d/1-g3qrPQgLSEf4EAF7lSF51oon1FUoZCw06Cc2ufK5_o/edit#slide=id.g2e7a2ec5a3f_0_107)


✏️ 작업순서
-

AWS Rekognition 공식 문서 확인 ➡︎ serverless 서버 생성 ➡︎ vsc 코드 개발 ➡︎ Postman 단위 테스트 ➡︎ github 레파지토리 생성 ➡︎ git Actions CI/CD 자동 배포 ➡︎ CloudWatch 로그 확인 후 디버깅 


✏️ Server 개발
-

Visual Studio Code를 사용해서 서버 개발 (Python)
- Framwork는 Flask, Serverless 사용했습니다.

서버 아키텍처
- AWS IAM, LAMBDA로 구성했습니다. 

VSC 폴더명으로 정리했습니다.
✉︎ APP.PY
- flask 를 사용하기 위한 코드 세팅
- Entry Point. api.add_resource 입력

✉︎ REKOGNITION.PY
- 얼굴 분석하는 코드
  
  : AWS IAM 권한을 주고 인공지능 Access key로 사용
  
  : boto3 라이브러리를 사용하여 사진이 AWS S3에 업데이트 되면 해당 사진을 분석
  
  ![얼굴 분석](https://github.com/user-attachments/assets/e31a2fe6-949c-4c80-b3c2-1f587a151e46)

- 얼굴 비교하는 코드
  
  : AWS IAM 권한을 주고 인공지능 Access key로 사용
  
  : boto3 라이브러리를 사용하여 비교할 두개의 사진을 AWS S3에 업데이트하고 compare_face 함수로 타겟 파일을 지정해 얼굴 비교
  
  ![얼굴 비교](https://github.com/user-attachments/assets/290d5d50-e033-4ab0-8319-bc5976349acd)




✏️ 배포
-

serverless, AWS LAMBDA,  AWS Later - pillow 사용해서 배포
: Docker 사용하지 않은 이유 -> 레이어 용량엔 한계가 있지만, pillow 라이브러리 한개만 올리면 되기 때문에 도커를 사용하지 않고 레이어에 넣어서 디버깅

github Actions로 git pull 자동화



✏️ 사용한 프로그램
-

<img src="https://img.shields.io/badge/Amazon AWS-232F3E?style=flat-square&logo=amazonaws&logoColor=white"/>
<img src="https://img.shields.io/badge/Visual Studio Code-007ACC?style=flat-square&logo=Visual Studio Code&logoColor=white"/>


<img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white"/> <img src="https://img.shields.io/badge/serverless-FD5750?style=flat-square&logo=serverless&logoColor=white"/>



✏️ 사용한 언어
-

<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=Python&logoColor=white"/>


