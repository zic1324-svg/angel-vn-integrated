# -*- coding: utf-8 -*-
import streamlit as st
import json, urllib.request
from pathlib import Path

st.set_page_config(
    page_title="엔젤베트남 영업 통합관리",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  .block-container { padding-top: 3rem !important; padding-bottom: 1rem; }

  /* 카드가 있는 컬럼: 상대 위치 기준 */
  [data-testid="stColumn"]:has(.home-card),
  [data-testid="stColumn"]:has(.npp-card),
  [data-testid="stColumn"]:has(.asm-card) { position: relative; }

  /* 투명 버튼을 카드 위에 덮어씌워서 전체 클릭 가능하게 */
  [data-testid="stColumn"]:has(.home-card) .stButton,
  [data-testid="stColumn"]:has(.npp-card) .stButton,
  [data-testid="stColumn"]:has(.asm-card) .stButton {
    position: absolute !important;
    top: 0 !important; left: 0 !important;
    width: 100% !important; height: 100% !important;
    z-index: 10 !important; margin: 0 !important; padding: 0 !important;
  }
  [data-testid="stColumn"]:has(.home-card) .stButton button,
  [data-testid="stColumn"]:has(.npp-card) .stButton button,
  [data-testid="stColumn"]:has(.asm-card) .stButton button {
    width: 100% !important; height: 100% !important;
    background: transparent !important; border: none !important;
    box-shadow: none !important; color: transparent !important;
    font-size: 0 !important; cursor: pointer !important;
  }
  [data-testid="stColumn"]:has(.home-card) .stButton button:hover,
  [data-testid="stColumn"]:has(.npp-card) .stButton button:hover,
  [data-testid="stColumn"]:has(.asm-card) .stButton button:hover {
    background: transparent !important;
  }

  /* 홈 카드 */
  .home-card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.2);
    border-radius: 16px; padding: 40px 24px; text-align: center;
    cursor: pointer; transition: all 0.2s; min-height: 200px;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
  }
  .home-card:hover { border-color: #4A9EFF; box-shadow: 0 4px 16px rgba(74,158,255,0.25); }
  .home-icon  { font-size: 3rem; margin-bottom: 12px; }
  .home-title { font-size: 1.15rem; font-weight: 700; margin-bottom: 6px; }
  .home-desc  { font-size: 0.83rem; color: #888; }

  /* NPP 카드 */
  .npp-card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.2);
    border-radius: 10px; padding: 16px; height: 130px; cursor: pointer;
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

  /* ASM 카드 */
  .asm-card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.2);
    border-radius: 12px; padding: 20px; text-align: center;
    min-height: 120px; cursor: pointer;
  }
  .asm-card:hover { border-color: #4A9EFF; box-shadow: 0 2px 8px rgba(74,158,255,0.2); }
  .asm-name { font-size: 1.0rem; font-weight: 700; margin-bottom: 6px; }
  .asm-sub  { font-size: 0.8rem; color: #888; }
  .asm-amt  { font-size: 1.1rem; font-weight: 700; color: #4A9EFF; margin-top: 8px; }

  hr.divider { border: none; border-top: 1px solid rgba(128,128,128,0.2); margin: 8px 0; }
  .breadcrumb { font-size: 0.82rem; color: #888; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# ── 상수 ────────────────────────────────────────────────────────────
TOKEN    = st.secrets["GIST_TOKEN"]
GIST_ID  = st.secrets["GIST_ID"]
FILENAME = "integrated_records.json"
LOCAL_DATA = Path(__file__).parent / "data" / "integrated_records.json"

SKU_LIST = ["BS VÀ HMP CŨ", "GIẶT XẢ", "PPSU", "KHĂN ƯỚT", "SỬA TẮM"]
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
        return json.loads(content) if content else {}, None
    except Exception as e:
        if LOCAL_DATA.exists():
            return json.loads(LOCAL_DATA.read_text(encoding="utf-8")), None
        return {}, str(e)

records, load_error = load_data()
if load_error:
    st.error(f"데이터 로드 실패: {load_error}")

# ── 세션 상태 초기화 ─────────────────────────────────────────────────
def init_state():
    defaults = {"page": "home", "selected_asm": None, "selected_npp": None, "month": 8}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

# ── 유틸 ────────────────────────────────────────────────────────────
def fmt(n):
    if n >= 1_000_000_000: return f"{n/1e9:.2f}tỷ"
    if n >= 1_000_000:     return f"{n/1e6:.1f}M"
    return f"{n:,.0f}"

def go(page, **kwargs):
    st.session_state.page = page
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.rerun()

def month_selector():
    available = sorted([int(k) for k in records.keys() if k.isdigit()])
    if not available:
        return None
    idx = available.index(st.session_state.month) if st.session_state.month in available else len(available)-1
    m = st.selectbox("월", available, index=idx, format_func=lambda x: f"{x}월", key="month_sel")
    st.session_state.month = m
    return m

def back_button(label, target, **kwargs):
    if st.button(f"← {label}", key=f"back_{target}"):
        go(target, **kwargs)

def sparkline_svg(values, width=120, height=32, color="#4A9EFF"):
    vals = list(values)
    if not any(vals):
        return f'<svg width="{width}" height="{height}"></svg>'
    mx = max(vals) or 1
    mn = min((v for v in vals if v > 0), default=0)
    rng = mx - mn or mx or 1
    pad = 4; w = width - pad*2; h = height - pad*2; n = len(vals)
    pts = []
    for i, v in enumerate(vals):
        x = pad + i * w / max(n-1, 1)
        y = pad + h - (v - mn)/rng*h if mx > 0 else pad + h
        pts.append(f"{x:.1f},{y:.1f}")
    polyline = " ".join(pts)
    fx, fy = pts[0].split(","); lx, ly = pts[-1].split(","); bot = pad + h
    fill_pts = f"{pts[0]} " + polyline + f" {lx},{bot} {fx},{bot}"
    return (
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
        f'<polygon points="{fill_pts}" fill="{color}" opacity="0.15"/>'
        f'<polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="{lx}" cy="{ly}" r="3" fill="{color}"/>'
        f'</svg>'
    )

# ────────────────────────────────────────────────────────────────────
# 페이지 함수들
# ────────────────────────────────────────────────────────────────────

def page_home():
    st.markdown("### 📊 엔젤베트남 영업 통합관리")
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class="home-card">
          <div class="home-icon">🏪</div>
          <div class="home-title">NPP별 재고관리</div>
          <div class="home-desc">NPP 재고 현황 및 관리</div>
        </div>""", unsafe_allow_html=True)
        if st.button("_", key="btn_npp", use_container_width=True):
            go("npp_inventory")
    with c2:
        st.markdown("""<div class="home-card">
          <div class="home-icon">📈</div>
          <div class="home-title">ASM별 세일아웃관리</div>
          <div class="home-desc">ASM 담당 NPP 세일아웃 현황</div>
        </div>""", unsafe_allow_html=True)
        if st.button("_", key="btn_asm", use_container_width=True):
            go("asm_saleout")
    with c3:
        st.markdown("""<div class="home-card">
          <div class="home-icon">👤</div>
          <div class="home-title">Sales별 매출관리</div>
          <div class="home-desc">세일즈맨 SKU별 실적 및 월별 추이</div>
        </div>""", unsafe_allow_html=True)
        if st.button("_", key="btn_sales", use_container_width=True):
            go("sales_asm")


def page_npp_inventory():
    back_button("홈으로", "home")
    st.markdown("## 🏪 NPP별 재고관리")
    st.info("재고 데이터를 업로드하면 활성화됩니다.")


def page_asm_saleout():
    back_button("홈으로", "home")
    st.markdown("## 📈 ASM별 세일아웃관리")

    col_m, col_s = st.columns([2, 6])
    with col_m:
        month = month_selector()
    if not month:
        st.warning("데이터가 없습니다."); return

    month_data = records.get(str(month), {})

    # ASM별 집계
    asm_totals = {}
    for code, d in month_data.items():
        asm = d.get("asm", "기타")
        asm_totals.setdefault(asm, {"total": 0, "npps": 0, "salesmen": set()})
        asm_totals[asm]["total"] += d.get("total", 0)
        asm_totals[asm]["npps"] += 1
        asm_totals[asm]["salesmen"].update(d.get("salesmen", {}).keys())

    sorted_asms = sorted(asm_totals.items(), key=lambda x: -x[1]["total"])

    st.markdown("---")
    COLS = 4
    rows = [sorted_asms[i:i+COLS] for i in range(0, len(sorted_asms), COLS)]
    for row in rows:
        cols = st.columns(COLS)
        for col, (asm_code, data) in zip(cols, row):
            full_name = ASM_FULL.get(asm_code, asm_code)
            with col:
                st.markdown(f"""
                <div class="asm-card">
                  <div class="asm-name">{asm_code}</div>
                  <div class="asm-sub">{full_name}</div>
                  <div class="asm-sub">NPP {data['npps']}개 · 세일즈맨 {len(data['salesmen'])}명</div>
                  <div class="asm-amt">{fmt(data['total'])}</div>
                </div>""", unsafe_allow_html=True)
                if st.button("상세보기", key=f"asm_{asm_code}", use_container_width=True):
                    go("asm_npp_list", selected_asm=asm_code)


def page_asm_npp_list():
    st.markdown(f'<div class="breadcrumb">홈 › ASM 세일아웃관리</div>', unsafe_allow_html=True)
    back_button("ASM 목록으로", "asm_saleout")

    asm_code = st.session_state.selected_asm
    full_name = ASM_FULL.get(asm_code, asm_code)

    col_m, col_t = st.columns([2, 6])
    with col_m:
        month = month_selector()
    if not month:
        return

    month_data = records.get(str(month), {})
    filtered = {k: v for k, v in month_data.items() if v.get("asm") == asm_code}

    st.markdown(f"### {asm_code} — {full_name}")
    total = sum(d["total"] for d in filtered.values())
    k1, k2 = st.columns(2)
    k1.metric("NPP 수", f"{len(filtered)}개")
    k2.metric(f"{month}월 합계", fmt(total))
    st.markdown("---")

    sorted_npps = sorted(filtered.items(), key=lambda x: -x[1]["total"])
    COLS = 4
    rows = [sorted_npps[i:i+COLS] for i in range(0, len(sorted_npps), COLS)]
    for row in rows:
        cols = st.columns(COLS)
        for col, (code, d) in zip(cols, row):
            name_short = d["name"][:38] + ("…" if len(d["name"]) > 38 else "")
            with col:
                st.markdown(f"""
                <div class="npp-card">
                  <div class="npp-title">{code}</div>
                  <div class="npp-name">{name_short}</div>
                  <div class="npp-meta">
                    <span class="npp-asm">{asm_code}</span>
                    <span class="npp-amt">{fmt(d["total"])}</span>
                  </div>
                </div>""", unsafe_allow_html=True)
                if st.button("상세보기", key=f"anpp_{code}", use_container_width=True):
                    go("sales_npp", selected_npp=code)


def page_sales_asm():
    back_button("홈으로", "home")
    st.markdown("## 👤 Sales별 매출관리")

    col_m, _ = st.columns([2, 6])
    with col_m:
        month = month_selector()
    if not month:
        st.warning("데이터가 없습니다."); return

    month_data = records.get(str(month), {})

    # ASM별 집계
    asm_totals = {}
    for code, d in month_data.items():
        asm = d.get("asm", "기타")
        asm_totals.setdefault(asm, {"total": 0, "npps": 0, "salesmen": set()})
        asm_totals[asm]["total"] += d.get("total", 0)
        asm_totals[asm]["npps"] += 1
        asm_totals[asm]["salesmen"].update(d.get("salesmen", {}).keys())

    sorted_asms = sorted(asm_totals.items(), key=lambda x: -x[1]["total"])

    st.markdown("---")
    COLS = 4
    rows = [sorted_asms[i:i+COLS] for i in range(0, len(sorted_asms), COLS)]
    for row in rows:
        cols = st.columns(COLS)
        for col, (asm_code, data) in zip(cols, row):
            full_name = ASM_FULL.get(asm_code, asm_code)
            with col:
                st.markdown(f"""
                <div class="asm-card">
                  <div class="asm-name">{asm_code}</div>
                  <div class="asm-sub">{full_name}</div>
                  <div class="asm-sub">NPP {data['npps']}개 · 세일즈맨 {len(data['salesmen'])}명</div>
                  <div class="asm-amt">{fmt(data['total'])}</div>
                </div>""", unsafe_allow_html=True)
                if st.button("ASM 선택", key=f"sasm_{asm_code}", use_container_width=True):
                    go("sales_npp_list", selected_asm=asm_code)


def page_sales_npp_list():
    st.markdown(f'<div class="breadcrumb">홈 › Sales 매출관리 › ASM 선택</div>', unsafe_allow_html=True)
    back_button("ASM 목록으로", "sales_asm")

    asm_code = st.session_state.selected_asm
    full_name = ASM_FULL.get(asm_code, asm_code)

    col_m, _ = st.columns([2, 6])
    with col_m:
        month = month_selector()
    if not month:
        return

    month_data = records.get(str(month), {})
    filtered = {k: v for k, v in month_data.items() if v.get("asm") == asm_code}

    st.markdown(f"### {asm_code} — {full_name} 담당 NPP")
    st.markdown("---")

    sorted_npps = sorted(filtered.items(), key=lambda x: -x[1]["total"])
    COLS = 4
    rows = [sorted_npps[i:i+COLS] for i in range(0, len(sorted_npps), COLS)]
    for row in rows:
        cols = st.columns(COLS)
        for col, (code, d) in zip(cols, row):
            name_short = d["name"][:38] + ("…" if len(d["name"]) > 38 else "")
            with col:
                st.markdown(f"""
                <div class="npp-card">
                  <div class="npp-title">{code}</div>
                  <div class="npp-name">{name_short}</div>
                  <div class="npp-meta">
                    <span class="npp-asm">{asm_code}</span>
                    <span class="npp-amt">{fmt(d["total"])}</span>
                  </div>
                </div>""", unsafe_allow_html=True)
                if st.button("세일즈맨 보기", key=f"snpp_{code}", use_container_width=True):
                    go("sales_npp", selected_npp=code)


def page_sales_npp():
    asm_code = st.session_state.selected_asm
    prev_page = "sales_npp_list" if asm_code else "sales_asm"
    prev_label = "NPP 목록으로" if asm_code else "ASM 목록으로"

    st.markdown(f'<div class="breadcrumb">홈 › Sales 매출관리 › {asm_code or ""} › NPP</div>', unsafe_allow_html=True)
    back_button(prev_label, prev_page)

    code = st.session_state.selected_npp
    col_m, _ = st.columns([2, 6])
    with col_m:
        month = month_selector()
    if not month:
        return

    month_data = records.get(str(month), {})
    npp = month_data.get(code)
    if not npp:
        st.warning(f"{month}월 데이터가 없습니다."); return

    asm = npp.get("asm", "")
    asm_name = ASM_FULL.get(asm, asm)
    st.markdown(f"### {code} — {npp['name']}")

    c1, c2, c3 = st.columns(3)
    c1.metric("ASM", f"{asm} ({asm_name})")
    c2.metric(f"{month}월 합계", fmt(npp["total"]))
    c3.metric("세일즈맨 수", len(npp.get("salesmen", {})))

    # SKU 합계
    st.markdown("---")
    sku_totals = {sku: 0 for sku in SKU_LIST}
    for sa_data in npp.get("salesmen", {}).values():
        for sku, amt in sa_data.get("skus", {}).items():
            if sku in sku_totals:
                sku_totals[sku] += amt
    cols = st.columns(len(SKU_LIST))
    for i, sku in enumerate(SKU_LIST):
        cols[i].metric(sku, fmt(sku_totals[sku]))

    # 세일즈맨 테이블
    st.markdown("---")
    st.markdown("### 세일즈맨별 실적")
    salesmen = npp.get("salesmen", {})
    sorted_sa = sorted(salesmen.items(), key=lambda x: -x[1].get("total", 0))

    header = st.columns([3, 1.2, 1.2, 1.2, 1.2, 1.2, 2])
    for col, label in zip(header, ["세일즈맨", "BS", "GIẶT XẢ", "PPSU", "KHĂN", "SỬA TẮM", "월별추이(1~8월)"]):
        col.markdown(f"**{label}**")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    for sa_name, sa_data in sorted_sa:
        skus = sa_data.get("skus", {})
        total = sa_data.get("total", 0)
        monthly = []
        for m in MONTHS:
            m_npp = records.get(str(m), {}).get(code, {})
            m_sa  = m_npp.get("salesmen", {}).get(sa_name, {})
            monthly.append(m_sa.get("total", 0))

        row = st.columns([3, 1.2, 1.2, 1.2, 1.2, 1.2, 2])
        display_name = sa_name.split("(NPP")[0].replace("Sale ", "").strip()
        row[0].markdown(f"**{display_name}**<br><small style='color:#888'>{fmt(total)}</small>", unsafe_allow_html=True)
        row[1].markdown(fmt(skus.get("BS VÀ HMP CŨ", 0)))
        row[2].markdown(fmt(skus.get("GIẶT XẢ", 0)))
        row[3].markdown(fmt(skus.get("PPSU", 0)))
        row[4].markdown(fmt(skus.get("KHĂN ƯỚT", 0)))
        row[5].markdown(fmt(skus.get("SỬA TẮM", 0)))
        svg = sparkline_svg(monthly[:8], width=140, height=36, color="#4A9EFF")
        row[6].markdown(svg, unsafe_allow_html=True)


# ── 라우팅 ───────────────────────────────────────────────────────────
PAGE_MAP = {
    "home":           page_home,
    "npp_inventory":  page_npp_inventory,
    "asm_saleout":    page_asm_saleout,
    "asm_npp_list":   page_asm_npp_list,
    "sales_asm":      page_sales_asm,
    "sales_npp_list": page_sales_npp_list,
    "sales_npp":      page_sales_npp,
}
PAGE_MAP.get(st.session_state.page, page_home)()
