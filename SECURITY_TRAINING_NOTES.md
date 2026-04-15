# Security training notes (safe)

이 레포는 **의도적으로 취약한 구현 코드를 제공하지 않습니다.**
대신 FastAPI 예제([app/main.py](app/main.py))는 기본적인 인증/인가 체크, 경로 검증 같은 **예방 패턴**을 포함하고,
아래는 각 취약점의 개념과 예방 포인트/테스트 아이디어를 고수준으로 정리합니다.

## 1) SQL Injection
- 개념: 문자열 연결로 SQL을 만들면 입력이 쿼리 구조를 바꿀 수 있음.
- 예방: 파라미터 바인딩(Prepared Statements), ORM의 바인딩 기능 사용, 입력 검증은 보조수단.
- 테스트 아이디어(고수준): 입력에 따옴표/연산자를 섞어도 쿼리 결과가 “구조적으로” 바뀌지 않아야 함.

## 2) Buffer Overflow
- 개념: C/C++ 등에서 경계 검사 없는 메모리 쓰기로 인한 메모리 손상.
- Python에서는 일반적으로 동일 유형의 버퍼 오버플로우가 잘 발생하지 않지만,
  네이티브 확장/FFI(예: C-extension, ctypes) 사용 시 위험이 생길 수 있음.
- 예방: 안전한 언어/라이브러리 사용, 길이 제한, 네이티브 코드 감사.

## 3) Broken Authentication
- 개념: 인증 토큰/세션 관리가 부실해 계정 탈취가 쉬워지는 상태.
- 예방: 강한 비밀번호 정책/해시(BCrypt/Argon2), 토큰 만료/회전, 안전한 쿠키 설정(HTTPS, HttpOnly, SameSite),
  로그인 시도 제한, MFA.
- 테스트 아이디어(고수준): 토큰 없이 접근이 차단되는지, 만료 후 재사용이 막히는지, 권한 상승이 안 되는지.

## 4) 민감정보 노출 (Sensitive Data Exposure)
- 개념: 로그/응답/리포지토리에 비밀번호·토큰·개인정보가 남는 문제.
- 예방: 비밀은 환경변수/시크릿 스토어로 주입, 로그/에러에서 민감정보 마스킹, 리포에 커밋 금지.
- 테스트 아이디어(고수준): 실패 응답/서버 로그에 토큰/패스워드가 포함되지 않는지 점검.

## 5) Insecure Deserialization
- 개념: 신뢰할 수 없는 입력을 역직렬화하면서 코드 실행/권한 상승으로 이어질 수 있음(특히 `pickle`).
- 예방: JSON 같은 안전한 포맷 사용, 스키마 검증(Pydantic), 서명된 데이터만 허용.
- 테스트 아이디어(고수준): 서버가 임의의 객체 그래프를 재구성하지 않고, 허용된 스키마만 받아들이는지.

## 6) IDOR (Insecure Direct Object Reference)
- 개념: 사용자가 소유하지 않은 리소스 ID를 지정해서 접근이 되는 문제.
- 예방: 모든 “객체 접근”에 대해 소유권/권한 확인.
- 예제: [app/main.py](app/main.py)의 `/users/{user_id}/profile`은 `user_id == current_user_id`를 강제합니다.

## 7) Path Traversal
- 개념: `../` 등으로 파일 경로를 탈출해 임의 파일을 읽는 문제.
- 예방: 허용 디렉터리 기준 `resolve()` 후 `relative_to()`로 경계 체크, 파일명 allowlist, 직접 경로 조합 최소화.
- 예제: [app/main.py](app/main.py)의 `/download/{name}`는 base dir 밖을 거부합니다.

## 스캔에서 "취약점이 보이게" 하는 방법(훈련용)
- 이 레포는 실제로 공격 가능한 취약 구현을 포함하지 않습니다.
- 대신 [security/semgrep.training.yml](security/semgrep.training.yml) 룰이 [vuln_markers/training_markers.py](vuln_markers/training_markers.py)의 마커 문자열을 탐지하면,
  SQLi/IDOR/Path Traversal 등 카테고리별로 **훈련용 finding**을 출력합니다.
- 실행(WSL): `./scripts/run_security_scan.sh`
