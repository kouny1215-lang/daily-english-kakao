# 📖 Daily English Kakao Bot 설정 가이드

매일 아침 7시(KST) 카카오톡 '나에게 보내기'로 오늘의 영어 레슨을 자동 발송합니다.

---

## 🎯 최종 결과물

매일 아침 카카오톡 "나와의 채팅방"에 이런 메시지가 도착합니다:

```
📖 The Daily English · 4월 19일
[리포팅·보고] 주간 업무 보고

🔑 핵심 표현
"Bottom line up front (BLUF)"
→ 결론부터 먼저. 바쁜 임원에게 보고할 때 핵심 전달 방식

💡 오늘의 단어
• on track — 계획대로 진행 중

📝 실전 문장
"Here's where we stand as of this week."
→ 이번 주 기준 현황은 다음과 같습니다.
```

---

## 📋 전체 설정 순서 (최초 1회, 약 1시간)

1. 카카오 개발자 앱 생성
2. 동의항목 및 Redirect URI 설정
3. 최초 토큰 발급 (로컬에서 Python 실행)
4. GitHub 저장소 생성 + 파일 업로드
5. GitHub Secrets에 토큰 등록
6. 테스트 실행 후 확인

---

## 🔧 STEP 1: 카카오 개발자 앱 생성 (10분)

1. https://developers.kakao.com 접속 → 카카오 계정으로 로그인
2. 상단 **내 애플리케이션** → **애플리케이션 추가하기**
3. 앱 이름: `Daily English` (자유), 사업자명: `개인` 입력 → 저장
4. 생성된 앱 클릭
5. **앱 설정 > 앱 키** 메뉴에서 **REST API 키** 복사해 메모해두기

## 🔧 STEP 2: 앱 설정 (10분)

### 2-1. 플랫폼 등록

1. 좌측 메뉴 **앱 설정 > 플랫폼**
2. **Web 플랫폼 등록** 클릭
3. 사이트 도메인: `http://localhost:3000` 입력 → 저장

### 2-2. Redirect URI 등록

1. 좌측 메뉴 **제품 설정 > 카카오 로그인**
2. **활성화 설정** → **ON**으로 변경
3. **Redirect URI** 항목 → **Redirect URI 등록**
4. `http://localhost:3000/callback` 입력 → 저장

### 2-3. 동의항목 설정

1. 좌측 메뉴 **제품 설정 > 카카오 로그인 > 동의항목**
2. **카카오톡 메시지 전송** (`talk_message`) 항목 찾기
3. 우측 **설정** → **선택 동의**로 저장

---

## 🔧 STEP 3: 최초 토큰 발급 (10분)

이 단계는 **로컬 PC**에서 실행합니다. Python 3이 설치되어 있어야 합니다.

### 3-1. 파일 다운로드

이 대화에서 받은 파일들을 로컬 PC의 빈 폴더에 모두 넣으세요:
- `send_daily_lesson.py`
- `get_initial_token.py`
- `lessons.json`
- `.github/workflows/daily.yml`
- `README.md`

### 3-2. get_initial_token.py 수정

텍스트 에디터로 `get_initial_token.py` 열고 `REST_API_KEY` 줄 수정:

```python
REST_API_KEY = "여기에_REST_API_키_입력"  # ← STEP 1에서 복사한 값
```

### 3-3. 실행

터미널에서 해당 폴더로 이동 후:

```bash
python get_initial_token.py
```

안내에 따라:
1. 출력된 URL을 브라우저에 복사해서 열기
2. 카카오 로그인 + 동의
3. "페이지를 찾을 수 없음" 화면이 떠도 OK — 주소창의 URL 확인
4. URL에서 `code=` 뒤의 값만 복사 (예: `?code=AbCdEf123...` → `AbCdEf123...`)
5. 터미널에 붙여넣기 → Enter

### 3-4. Refresh Token 저장

출력된 `KAKAO_REFRESH_TOKEN` 값을 잘 보관하세요. 다음 단계에서 사용합니다.

⚠️ 이 값은 **다른 사람에게 절대 공유하지 마세요**. 외부 노출 시 카톡 전송 권한이 넘어갑니다.

---

## 🔧 STEP 4: GitHub 저장소 생성 및 업로드 (15분)

### 4-1. 저장소 생성

1. https://github.com 로그인
2. 우측 상단 **+** → **New repository**
3. Repository name: `daily-english-kakao` (자유)
4. **Private** 선택 (보안)
5. **Create repository** 클릭

### 4-2. 파일 업로드

**방법 A: 웹 UI 업로드 (가장 쉬움)**

1. 생성된 저장소 페이지에서 **uploading an existing file** 클릭
2. `send_daily_lesson.py`, `lessons.json`, `README.md` 드래그
3. **Commit changes** 클릭
4. 다시 저장소 루트로 와서 **Add file > Create new file** 클릭
5. 파일명 입력란에 `.github/workflows/daily.yml` 입력 (슬래시가 자동으로 폴더를 만듭니다)
6. 파일 내용에 `daily.yml` 내용 붙여넣기
7. **Commit new file** 클릭

**방법 B: git 명령어**

```bash
cd 파일_있는_폴더
git init
git add send_daily_lesson.py lessons.json README.md .github/
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/사용자명/daily-english-kakao.git
git push -u origin main
```

⚠️ **주의**: `get_initial_token.py`는 **올리지 마세요**. REST API 키가 하드코딩되어 있어요. 로컬에만 두세요.

---

## 🔧 STEP 5: GitHub Secrets 등록 (5분)

1. 저장소 페이지에서 **Settings** 탭 클릭
2. 좌측 **Secrets and variables > Actions**
3. **New repository secret** 클릭
4. 두 개의 secret 등록:

   | Name | Value |
   |---|---|
   | `KAKAO_REST_API_KEY` | STEP 1에서 복사한 REST API 키 |
   | `KAKAO_REFRESH_TOKEN` | STEP 3에서 받은 Refresh Token |

---

## 🔧 STEP 6: 테스트 실행 (5분)

1. 저장소의 **Actions** 탭 클릭
2. "I understand my workflows, go ahead and enable them" 버튼이 보이면 클릭 (첫 1회만)
3. 좌측에서 **Daily English Lesson** 워크플로우 선택
4. 우측 **Run workflow** 버튼 → **Run workflow** 클릭
5. 1분쯤 후 실행 결과 확인 (녹색 체크면 성공)
6. **카카오톡 → 나와의 채팅**에 메시지가 왔는지 확인 🎉

---

## 🎉 완료!

이제 매일 아침 7시(KST)에 자동으로 오늘의 영어 레슨이 카톡으로 옵니다.

---

## ❓ FAQ

**Q: 시간을 바꾸고 싶어요**
A: `.github/workflows/daily.yml`의 `cron: '0 22 * * *'` 수정.
예: 오전 8시 → `0 23 * * *` (UTC는 KST -9시간)

**Q: 레슨을 추가하고 싶어요**
A: `lessons.json`의 `lessons` 배열에 같은 구조로 추가 후 commit.

**Q: 메시지가 200자를 넘어요**
A: 카카오 default 텍스트 템플릿의 제한입니다. 스크립트가 자동으로 자르지만,
더 긴 내용을 보내려면 'feed' 또는 'list' 템플릿으로 변경 필요.

**Q: Refresh Token이 만료되나요?**
A: 2개월 내 사용이 있으면 자동 갱신됩니다. 매일 발송하므로 문제없어요.

**Q: GitHub Actions가 안 돌아가요**
A: 60일간 저장소에 아무 활동(commit/push)이 없으면 자동 비활성화됩니다.
매일 실행되니 문제 없지만, 비활성화 시 Actions 탭에서 재활성화 가능.

**Q: 레슨 레벨이나 카테고리 선택권을 원해요**
A: "선택 귀찮음" 해결이 목적이므로 완전 랜덤으로 설정했습니다.
특정 카테고리만 받고 싶으시면 `pick_lesson` 함수에서 필터링 가능.

---

## 🔒 보안 주의사항

- `get_initial_token.py`에 하드코딩한 REST API 키는 Git에 커밋하지 마세요
- Refresh Token은 GitHub Secrets 외에 노출되지 않아야 합니다
- 저장소는 **Private**으로 유지하세요
