# 🚀 프로젝트 소개
> 다양한 도메인의 테이블 데이터에 대해서 EDA부터 솔루션 까지 제공하는 Prescriptive AI를 제공합니다.

### 팀의 주제 소개
> 이직률 데이터를 활용하여 이직시 발생하는 피해를 최소화 하기 위한 솔루션을 제공한다.
> Autogluon 라이브러리를 활용하여 다양한 데이터에 최적화된 surrogate model을 생성하고 Oputna, LLM을 활용하여 최적의 솔루션을 제공하는 것을 목표로 하고 있습니다. <br>
> 관련 뉴스 : https://www.mk.co.kr/news/business/10551056
<br>

# 📁 Dataset
[Kaggle Dataset] : https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset


<br>


# 💁🏼‍♂️💁‍♀️ 멤버 소개
| 이름       | 기여 내용 |
|------------|-----------|
| **김한별** | - 데이터 전처리 자동화 보조, AutoML과 최적화 과정 고도화  |
| **손지형** | - 데이터 전처리 자동화,  config관리 및 자동 업데이트 |
| **유지환** | - 웹 서비스 개발 보조 |
| **정승민** | - AutoML과 최적화 과정 구현 및 고도화, GPT 솔루션 제공 과정 구현  |
| **조현준** | - 웹 서비스 개발(프론트엔드, 백엔드)  |


<br>

# 📅 프로젝트 타임라인

| **Week** | **Data Preprocessing**                 | **Model**                                   | **Web Service**              |
|----------|--------------------------------------|-------------------------------------------|-----------------------------|
| **Week 1** | 전처리 자동화 설계 및 구현          | 예측 모델 + 최적화 과정 baseline 구축       | 백엔드 API 개발              |
| **Week 2** | 모든 데이터 셋 처리 가능하게 수정   | 최적화 과정 고도화                        | 프론트엔드 - 백엔드 연동     |
| **Week 3** | 디코딩 오류 해결 및 안정성 개선     | 웹 연동을 위한 코드 리팩토링, GPT 솔루션 적용 | 백엔드 - 모델 연동            |



<br>

# 🖥️ 프로젝트 진행 환경

### 하드웨어
- **GPU**: NVIDIA Tesla V100-SXM2 32GB
  - **메모리**: 32GB

### 소프트웨어
- **Driver Version**: 535.161.08
- **CUDA Version**: 12.2
- **Python Version**: 3.10.13

### 라이브러리
- Optuna : https://optuna.org/
- Autogluon : https://auto.gluon.ai/stable/index.html

### LLM Model
- Open AI gpt-4o API


<br>

# 🧰 필요한 라이브러리 설치
```bash
pip install requirements.txt
```



<br>


# ⚙️ 사용방법 ( 터미널 ) 
```bash
export PYTHONPATH=$(pwd)
python process/process.py
```
> LLM 사용시 gpt.py에 API 키를 입력해주세요. <br>
> process.py의 process2, process3의 함수에 각 데이터에 맞는 변수들을 설정해주세요.

<br>

# 🗂️ 파일구조
📂 프로젝트 폴더
```plaintext
📂 프로젝트 루트
│── 📂 config
│   ├── __init__.py
│   ├── config_generator.py
│   ├── update_config.py
│
│── 📂 data
│   ├── data_preprocess.py
│   ├── model_input_builder.py
│
│── 📂 fastapi-ca
│
│── 📂 frontend
│
│── 📂 model
│   ├── auto_ml.py
│   ├── regression_metrics.py
│
│── 📂 optimization
│   ├── feature_optimization.py
│   ├── optimization.py
│
│── 📂 process
│   ├── process.py
│
│── 📂 user_input
│   ├── setting_input.py
│
│── 📂 utils
│   ├── analysis_feature.py
│   ├── determine_feature.py
│   ├── logger_config.py
│   ├── print_feature_type.py
│   ├── setting.py
│   ├── user_feature.py
│
│── .gitignore
│── gpt.py
│── README.md
│── requirements.txt
```

<br>

# 모델 파이프라인

<img width="922" alt="image" src="https://github.com/user-attachments/assets/b0822afa-11f0-4c26-8be5-0104f7523a5e" />

# 성능 지표

| 지표       | 02조    | 06조    | 17조    | 22조    |
|------------|---------|---------|---------|---------|
| MSE        | -0.162  | -0.1511 | -0.1525 | -0.1923 |
| R square   | 0.8319  | 0.9402  | 0.977   | 0.8031  |
| pearsonr   | 0.9121  | 0.97    | 0.9885  | 0.8329  |
| Median_AE  | -0.2142 | -0.085  | -1.5987 | -2.034  |
| RMSE       | 0.4025  | -0.2477 | -0.1511 | 0.7231  |

<br>

# 📞 문의
김한별 : 2002bigstar@gmail.com  <br> 손지형 : sonji0988@gmail.com  <br> 유지환 : harwsare@yonsei.ac.kr  <br> 정승민 : taky0315@naver.com  <br> 조현준 : aaiss0927@gamil.com   <br>


