서울 무더위쉼터 접근성 · 과제 3

[Cloudflare Pages 업로드]
1. Cloudflare 로그인 → Workers & Pages → Create application → Pages → Use direct upload.
2. 프로젝트 이름 입력(예: seoul-cooling-access).
3. 제공된 ZIP을 그대로 업로드하거나, 압축을 풀어 index.html이 들어 있는 폴더를 업로드.
4. Deploy site 클릭. 발급된 https://프로젝트명.pages.dev 주소를 과제 제출란에 입력.
ZIP 최상위에 index.html이 있어야 합니다. GitHub 연결이나 빌드 명령은 필요 없습니다.
기존 Git 연동 프로젝트는 새 Direct Upload 프로젝트와 경로가 다를 수 있습니다.
공식 안내: https://developers.cloudflare.com/pages/get-started/direct-upload/

[미리 보기]
ZIP을 풀고 index.html을 브라우저에서 엽니다. 지도/데이터는 모두 로컬 파일이며 외부 API 키가 필요 없습니다.
스타일과 data.js, app.js 파일을 함께 유지하세요.

[분석]
2026 등록 쉼터, 2024 100m 격자인구, 2025.06.30 행정동 경계.
수요일/일요일 오후 2시 운영 일정, 300/500/800m 직선거리 접근 인구 비율.
전체 등록시설 / 공공시설 분류를 비교할 수 있습니다.
운영시간이 같게 기재된 일정은 24시간으로 추정하지 않았습니다.
수용능력, 실제 개방, 이용 자격, 계절 조건, 실제 보행망은 측정하지 않습니다.

[재현]
Python 패키지: research/requirements.txt
교수님 저장소: https://github.com/jslee-gses/code
확인한 커밋: d04422c9a8341df75795956db6bdec4aaa9a61e0
재실행 예시:
python -m pip install -r research/requirements.txt
python research/analyze.py --base /path/to/code/lecture05_urban_planning_index
원본 쉼터 CSV는 research/shelters_original.csv(CP949)에 포함.
분석 스크립트가 data.js, dong_results.csv, research/grid_results.csv, research/audit.json을 생성합니다.
본문의 고정 결과 문구는 재분석 시 결과에 맞춰 갱신해야 합니다.

[구성]
index.html / style.css / app.js / data.js: 웹페이지
 dong_results.csv: 모든 조건의 426개 행정동 결과
 research/analyze.py: 공간 분석 및 집계 코드
 research/grid_results.csv: 격자별 최근접 거리와 인구
 research/audit.json: 검증 수치

[출처]
서울특별시, 서울 열린데이터광장 '서울시 무더위쉼터', 공공누리 제1유형 출처표시.
https://data.seoul.go.kr/dataList/OA-21065/S/1/datasetView.do
인구/경계: 교수님 실습 저장소 제공자료. SGIS 등 원출처는 실습 노트북 참조.
AI 보조: 코드 작성·검증 및 페이지 제작. 모든 수치는 제공 원자료를 이용해 계산.
