# -*- coding: utf-8 -*-
import streamlit as st
import json, urllib.request, urllib.error
from pathlib import Path

st.set_page_config(
    page_title="엔젤베트남 영업 통합관리",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 스타일 ──────────────────────────────────────────────────────────
st.markdown("""
<style>
  .block-container { padding-top: 1rem; padding-bottom: 1rem; }
  .npp-card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.2);
    border-radius: 10px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.15s;
    height: 130px;
  }
  .npp-card:hover { border-color: #4A9EFF; box-shadow: 0 2px 8px rgba(74,158,255,0.2); }
  .npp-title { font-size: 0.78rem; color: #888; margin-bottom: 4px; font-family: monospace; }
  .npp-name  { font-size: 0.9rem; font-weight: 600; line-height: 1.3; margin-bottom: 8px;
               overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2;
               -webkit-box-orient: vertical; }
  .npp-meta  { display: flex; justify-content: space-between; align-items: center; }
  .npp-asm   { font-size: 0.75rem; background: #1E3A5F; color: #7EB8FF;
               padding: 2px 8px; border-radius: 20px; }
  .npp-amt   { font-size: 1.0rem; font-weight: 700; color: #4A9EFF; }
  .sku-chip  { display: inline-block; font-size: 0.72rem; padding: 2px 7px;
               border-radius: 12px; margin: 2px; }
  .sparkline { width: 100%; height: 36px; }
  hr.divider { border: none; border-top: 1px solid rgba(128,128,128,0.2); margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# ── 상수 ────────────────────────────────────────────────────────────
TOKEN    = st.secrets["GIST_TOKEN"]
GIST_ID  = st.secrets["GIST_ID"]
FILENAME = "integrated_records.json"
APP_PASS = st.secrets["APP_PASSWORD"]
LOCAL_DATA = Path(__file__).parent / "data" / "integrated_records.json"

SKU_LIST = ["BS VÀ HMP CŨ", "GIẶT XẢ", "PPSU", "KHĂN ƯỚT", "SỬA TẮM"]
SKU_COLOR = {
    "BS VÀ HMP CŨ": "#4A9EFF",
    "GIẶT XẢ":      "#34D399",
    "PPSU":         "#FBBF24",
    "KHĂN ƯỚT":     "#A78BFA",
    "SỬA TẮM":      "#FB7185",
}
ASM_FULL = {
    'NHU':'Nguyễn Văn Như','HAI':'Diệp Thế Hải','VINH':'Nguyễn Văn Vịnh',
    'LAM':'Kiều Phú Lâm','QUOC':'Nguyễn Minh Quốc','TU':'Nguyễn Hữu Bảy Tú',
    'HUNG':'Trần Văn Thanh Hùng','VAN':'Mai Hà Văn','TU,HOI':'Phan Đức Hạnh',
}
MONTHS = list(range(1, 13))

# ── 데이터 로드 ──────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    try:
        req = urllib.request.Request(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={"Authorization": f"token {TOKEN}",
                     "Accept": "application/vnd.github.v3+json"})
        g = json.loads(urllib.request.urlopen(req, timeout=10).read())
        content = g["files"][FILENAME]["content"]
        return json.loads(content) if content else {}
    except Exception:
        if LOCAL_DATA.exists():
            return json.loads(LOCAL_DATA.read_text(encoding="utf-8"))
        return {}

# ── 세션 상태 초기화 ─────────────────────────────────────────────────
if "auth" not in st.session_state:
    st.session_state.auth = False
if "page" not in st.session_state:
    st.session_state.page = "main"
if "selected_npp" not in st.session_state:
    st.session_state.selected_npp = None
if "month" not in st.session_state:
    st.session_state.month = 8

# ── 로그인 ───────────────────────────────────────────────────────────
if not st.session_state.auth:
    st.title("📊 엔젤베트남 영업 통합관리")
    st.markdown("---")
    col = st.columns([1, 2, 1])[1]
    with col:
        pw = st.text_input("비밀번호", type="password")
        if st.button("로그인", use_container_width=True):
            if pw == APP_PASS:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")
    st.stop()

# ── 데이터 로드 ──────────────────────────────────────────────────────
records = load_data()

# ── 스파크라인 SVG ───────────────────────────────────────────────────
def sparkline_svg(values, width=120, height=32, color="#4A9EFF"):
    vals = [v for v in values]
    if not any(vals):
        return f'<svg width="{width}" height="{height}"></svg>'
    mx = max(vals) or 1
    mn = min(v for v in vals if v > 0) if any(v > 0 for v in vals) else 0
    rng = mx - mn or mx or 1
    pad = 4
    w = width - pad * 2
    h = height - pad * 2
    n = len(vals)
    pts = []
    for i, v in enumerate(vals):
        x = pad + i * w / max(n - 1, 1)
        y = pad + h - (v - mn) / rng * h if mx > 0 else pad + h
        pts.append(f"{x:.1f},{y:.1f}")
    polyline = " ".join(pts)
    # fill area
    first_x, first_y = pts[0].split(",")
    last_x,  last_y  = pts[-1].split(",")
    bottom = pad + h
    fill_pts = f"{pts[0]} " + polyline + f" {last_x},{bottom} {first_x},{bottom}"
    return (
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
        f'<polygon points="{fill_pts}" fill="{color}" opacity="0.15"/>'
        f'<polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="{last_x}" cy="{last_y}" r="3" fill="{color}"/>'
        f'</svg>'
    )

def fmt(n):
    if n >= 1_000_000_000:
        return f"{n/1e9:.2f}tỷ"
    return f"{n/1e6:.1f}M"

# ── 상세 페이지 ──────────────────────────────────────────────────────
def page_detail():
    code = st.session_state.selected_npp
    month = st.session_state.month

    # 뒤로가기
    if st.button("← NPP 목록으로"):
        st.session_state.page = "main"
        st.rerun()

    month_data = records.get(str(month), {})
    npp = month_data.get(code)
    if not npp:
        st.warning(f"{month}월 데이터가 없습니다.")
        return

    asm_code = npp.get("asm", "")
    asm_name = ASM_FULL.get(asm_code, asm_code)
    st.markdown(f"## {code}")
    st.markdown(f"**{npp['name']}**")

    c1, c2, c3 = st.columns(3)
    c1.metric("ASM", f"{asm_code} — {asm_name}")
    c2.metric(f"{month}월 합계", fmt(npp["total"]))
    c3.metric("세일즈맨 수", len(npp.get("salesmen", {})))

    # SKU별 합계
    st.markdown("---")
    sku_totals = {sku: 0 for sku in SKU_LIST}
    for sa_data in npp.get("salesmen", {}).values():
        for sku, amt in sa_data.get("skus", {}).items():
            if sku in sku_totals:
                sku_totals[sku] += amt
    cols = st.columns(len(SKU_LIST))
    for i, sku in enumerate(SKU_LIST):
        cols[i].metric(sku, fmt(sku_totals[sku]))

    # 세일즈맨 테이블 + 스파크라인
    st.markdown("---")
    st.markdown("### 세일즈맨별 실적")

    salesmen = npp.get("salesmen", {})
    sorted_sa = sorted(salesmen.items(), key=lambda x: -x[1].get("total", 0))

    header = st.columns([3, 1.2, 1.2, 1.2, 1.2, 1.2, 2])
    for col, label in zip(header, ["세일즈맨", "BS", "GIẶT XẢ", "PPSU", "KHĂN", "SỬA TẮM", "월별추이"]):
        col.markdown(f"**{label}**")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    for sa_name, sa_data in sorted_sa:
        skus = sa_data.get("skus", {})
        total = sa_data.get("total", 0)

        # 이 세일즈맨의 월별 합계 (모든 월)
        monthly = []
        for m in MONTHS:
            m_npp = records.get(str(m), {}).get(code, {})
            m_sa  = m_npp.get("salesmen", {}).get(sa_name, {})
            monthly.append(m_sa.get("total", 0))

        row = st.columns([3, 1.2, 1.2, 1.2, 1.2, 1.2, 2])
        # 이름에서 "(NPP ...)" 부분 제거해서 표시
        display_name = sa_name.split("(NPP")[0].replace("Sale ", "").strip()
        row[0].markdown(f"**{display_name}**<br><small style='color:#888'>{fmt(total)}</small>",
                        unsafe_allow_html=True)
        row[1].markdown(fmt(skus.get("BS VÀ HMP CŨ", 0)))
        row[2].markdown(fmt(skus.get("GIẶT XẢ", 0)))
        row[3].markdown(fmt(skus.get("PPSU", 0)))
        row[4].markdown(fmt(skus.get("KHĂN ƯỚT", 0)))
        row[5].markdown(fmt(skus.get("SỬA TẮM", 0)))
        svg = sparkline_svg(monthly, width=120, height=32, color="#4A9EFF")
        row[6].markdown(svg, unsafe_allow_html=True)

# ── 메인 페이지 ──────────────────────────────────────────────────────
def page_main():
    # 헤더
    c_title, c_month, c_asm, c_search = st.columns([3, 1.5, 1.5, 2])
    c_title.markdown("## 📊 엔젤베트남 영업통합관리")

    available_months = sorted([int(k) for k in records.keys() if k.isdigit()])
    if not available_months:
        st.warning("데이터가 없습니다.")
        return

    default_idx = available_months.index(st.session_state.month) \
                  if st.session_state.month in available_months else len(available_months) - 1
    month = c_month.selectbox("월", available_months,
                              index=default_idx,
                              format_func=lambda m: f"{m}월")
    st.session_state.month = month

    month_data = records.get(str(month), {})

    all_asms = sorted(set(d.get("asm", "") for d in month_data.values() if d.get("asm")))
    asm_sel = c_asm.selectbox("ASM", ["전체"] + all_asms)
    search  = c_search.text_input("NPP 검색", placeholder="코드 또는 이름...")

    st.markdown("---")

    # 필터
    filtered = {
        code: d for code, d in month_data.items()
        if (asm_sel == "전체" or d.get("asm") == asm_sel)
        and (not search or search.lower() in code.lower() or search.lower() in d.get("name","").lower())
    }

    # 요약 KPI
    total_amt   = sum(d["total"] for d in filtered.values())
    total_npps  = len(filtered)
    total_sa    = len(set(sa for d in filtered.values() for sa in d.get("salesmen", {})))
    k1, k2, k3 = st.columns(3)
    k1.metric("NPP 수", f"{total_npps}개")
    k2.metric("세일아웃 합계", fmt(total_amt))
    k3.metric("세일즈맨 수", f"{total_sa}명")

    st.markdown("---")

    # NPP 카드 그리드 (4열)
    sorted_npps = sorted(filtered.items(), key=lambda x: -x[1]["total"])
    COLS = 4
    rows = [sorted_npps[i:i+COLS] for i in range(0, len(sorted_npps), COLS)]

    for row in rows:
        cols = st.columns(COLS)
        for col, (code, d) in zip(cols, row):
            asm = d.get("asm", "")
            name_short = d["name"][:40] + ("…" if len(d["name"]) > 40 else "")
            with col:
                st.markdown(f"""
                <div class="npp-card">
                  <div class="npp-title">{code}</div>
                  <div class="npp-name">{name_short}</div>
                  <div class="npp-meta">
                    <span class="npp-asm">{asm}</span>
                    <span class="npp-amt">{fmt(d["total"])}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("상세보기", key=f"btn_{code}", use_container_width=True):
                    st.session_state.selected_npp = code
                    st.session_state.page = "detail"
                    st.rerun()

# ── 라우팅 ───────────────────────────────────────────────────────────
if st.session_state.page == "detail" and st.session_state.selected_npp:
    page_detail()
else:
    st.session_state.page = "main"
    page_main()
