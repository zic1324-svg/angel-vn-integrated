"""ASM 계정 비밀번호를 angel2026으로 초기화하는 관리자 스크립트.
사용법: python reset_asm_password.py <LOGIN_ID>
예: python reset_asm_password.py NHU

환경변수 GIST_TOKEN이 설정되어 있어야 합니다.
없으면 스크립트 실행 시 직접 입력합니다.
"""
import sys, json, hashlib, urllib.request, os, getpass

GIST_TOKEN = os.environ.get("GIST_TOKEN") or getpass.getpass("GIST_TOKEN: ")
GIST_ID    = "3e02c404603ba04dca00c1c925211cba"
PW_FILE    = "asm_passwords.json"
DEFAULT_PW = "angel2026"

VALID_IDS = ['NHU','HAI','VINH','LAM','QUOC','TU','HUNG','VAN','TUHOI']

def main():
    if len(sys.argv) < 2:
        print("사용법: python reset_asm_password.py <LOGIN_ID>")
        print(f"유효한 ID: {', '.join(VALID_IDS)}")
        sys.exit(1)

    login_id = sys.argv[1].strip().upper()
    if login_id not in VALID_IDS:
        print(f"오류: '{login_id}'는 유효하지 않은 계정 ID입니다.")
        print(f"유효한 ID: {', '.join(VALID_IDS)}")
        sys.exit(1)

    headers = {
        "Authorization": f"token {GIST_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    # 현재 비밀번호 파일 로드
    req = urllib.request.Request(f"https://api.github.com/gists/{GIST_ID}", headers=headers)
    g = json.loads(urllib.request.urlopen(req, timeout=10).read())
    f = g.get("files", {}).get(PW_FILE, {})
    if f.get("truncated"):
        rr = urllib.request.Request(f["raw_url"], headers=headers)
        pws = json.loads(urllib.request.urlopen(rr, timeout=15).read())
    else:
        pws = json.loads(f.get("content", "{}"))

    # 초기화
    new_hash = hashlib.sha256(DEFAULT_PW.encode()).hexdigest()
    pws[login_id] = new_hash

    # Gist 업데이트
    patch_headers = {**headers, "Content-Type": "application/json"}
    payload = json.dumps({
        "files": {PW_FILE: {"content": json.dumps(pws, ensure_ascii=False)}}
    }).encode()
    patch_req = urllib.request.Request(
        f"https://api.github.com/gists/{GIST_ID}",
        data=payload, headers=patch_headers, method="PATCH")
    urllib.request.urlopen(patch_req, timeout=10)

    print(f"✅ {login_id} 비밀번호가 '{DEFAULT_PW}'(으)로 초기화되었습니다.")

if __name__ == "__main__":
    main()
