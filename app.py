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

  a { text-decoration: none !important; color: inherit !important; }

  .home-card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.2);
    border-radius: 16px; padding: 40px 24px; text-align: center;
    cursor: pointer; transition: border-color 0.2s, box-shadow 0.2s;
    min-height: 220px; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
  }
  .home-card:hover { border-color: #4A9EFF; box-shadow: 0 4px 16px rgba(74,158,255,0.25); }
  .home-icon  { font-size: 3rem; margin-bottom: 14px; }
  .home-title { font-size: 1.15rem; font-weight: 700; margin-bottom: 6px; }
  .home-desc  { font-size: 0.83rem; color: #888; }

  .npp-card-wrap {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.2);
    border-radius: 10px; overflow: hidden; min-height: 130px;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .npp-card-wrap:hover { border-color: rgba(74,158,255,0.4); box-shadow: 0 2px 8px rgba(74,158,255,0.1); }
  .npp-card-hdr { padding: 14px 14px 10px; }
  .npp-card-body { display: flex; border-top: 1px solid rgba(128,128,128,0.15); }
  .npp-title { font-size: 0.83rem; color: #888; margin-bottom: 4px; font-family: monospace; }
  .npp-name  { font-size: 1.0rem; font-weight: 600; line-height: 1.3;
               overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2;
               -webkit-box-orient: vertical; }
  .npp-half {
    flex: 1; padding: 10px 14px; display: block;
    transition: background 0.15s; cursor: pointer;
  }
  .npp-half:hover { background: rgba(74,158,255,0.08); }
  .npp-half-left  { border-right: 1px solid rgba(128,128,128,0.15); }
  .npp-half-lbl   { font-size: 0.78rem; color: #888; margin-bottom: 4px; }
  .npp-half-amt   { font-size: 1.05rem; font-weight: 700; color: #4A9EFF; }
  .npp-half-inv   { color: #52c41a; }
  .npp-half-months      { font-size: 0.8rem; color: #888;    margin-top: 3px; }
  .npp-half-months-warn { font-size: 0.8rem; color: #ff7875; margin-top: 3px; font-weight: 600; }

  .asm-card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.2);
    border-radius: 12px; padding: 20px; text-align: center;
    min-height: 130px; cursor: pointer;
    transition: border-color 0.2s, box-shadow 0.2s; display: block;
  }
  .asm-card:hover { border-color: #4A9EFF; box-shadow: 0 2px 8px rgba(74,158,255,0.2); }
  .asm-name { font-size: 1.0rem; font-weight: 700; margin-bottom: 6px; }
  .asm-sub  { font-size: 0.8rem; color: #888; line-height: 1.6; }
  .asm-amt  { font-size: 1.1rem; font-weight: 700; color: #4A9EFF; margin-top: 8px; }

  hr.divider { border: none; border-top: 1px solid rgba(128,128,128,0.2); margin: 8px 0; }
  .breadcrumb { font-size: 0.82rem; color: #888; margin-bottom: 4px; }

  .nav-back {
    display: inline-block; margin-bottom: 12px;
    font-size: 0.85rem; color: #888; text-decoration: none !important;
    border: 1px solid rgba(128,128,128,0.35); border-radius: 6px;
    padding: 4px 12px; transition: border-color 0.2s, color 0.2s;
  }
  .nav-back:hover { color: #ccc !important; border-color: rgba(128,128,128,0.6); }
  .nav-home {
    display: inline-block; margin-bottom: 12px; margin-left: 8px;
    font-size: 0.85rem; color: #fff !important; text-decoration: none !important;
    background: #4A9EFF; border-radius: 6px; padding: 4px 12px;
    transition: background 0.2s;
  }
  .nav-home:hover { background: #2f86f0; }
</style>
""", unsafe_allow_html=True)

# ── 상수 ────────────────────────────────────────────────────────────
TOKEN        = st.secrets["GIST_TOKEN"]
GIST_ID      = st.secrets["GIST_ID"]
FILENAME     = "integrated_records.json"
INV_FILENAME = "inventory_records.json"
LOCAL_DATA   = Path(__file__).parent / "data" / "integrated_records.json"
LOCAL_INV    = Path(__file__).parent / "data" / "inventory_records.json"

SKU_LIST = ["BS VÀ HMP CŨ", "GIẶT XẢ", "PPSU", "KHĂN ƯỚT", "SỮA TẮM"]
SKU_ICONS = {
    "BS VÀ HMP CŨ": "🍼",
    "GIẶT XẢ":      "👕",
    "PPSU":         "👑",
    "KHĂN ƯỚT":    "🧻",
    "SỮA TẮM":     "🛁",
}

REGION_MAP = {
    "AGI":"Tỉnh An Giang","BDI":"Tỉnh Bình Định","BDU":"Tỉnh Bình Dương","BGI":"Tỉnh Bắc Giang",
    "BLI":"Tỉnh Bạc Liêu","BNI":"Tỉnh Bắc Ninh","BPH":"Tỉnh Bình Phước","BRV":"Tỉnh Bà Rịa - Vũng Tàu",
    "BTH":"Tỉnh Bình Thuận","BTR":"Tỉnh Bến Tre","CMA":"Tỉnh Cà Mau","CTH":"Thành phố Cần Thơ",
    "DLA":"Tỉnh Đắk Lắk","DNA":"Thành phố Đà Nẵng","DNO":"Tỉnh Đắk Nông","DON":"Tỉnh Đồng Nai",
    "DTH":"Tỉnh Đồng Tháp","GLA":"Tỉnh Gia Lai","HAN":"Thành phố Hà Nội","HCM":"Thành phố Hồ Chí Minh",
    "HGI":"Tỉnh Hà Giang","HPH":"Thành phố Hải Phòng","HTI":"Tỉnh Hà Tĩnh","HUE":"Tỉnh Thừa Thiên - Huế",
    "HYE":"Tỉnh Hưng Yên","KGI":"Tỉnh Kiên Giang","KHH":"Tỉnh Khánh Hòa","LAN":"Tỉnh Long An",
    "LCA":"Tỉnh Lào Cai","LDO":"Tỉnh Lâm Đồng","NAN":"Tỉnh Nghệ An","NBI":"Tỉnh Ninh Bình",
    "NDI":"Tỉnh Nam Định","PTH":"Tỉnh Phú Thọ","QBI":"Tỉnh Quảng Bình","QNA":"Tỉnh Quảng Nam",
    "QNG":"Tỉnh Quảng Ngãi","QNI":"Tỉnh Quảng Ninh","QTR":"Tỉnh Quảng Trị","STR":"Tỉnh Sóc Trăng",
    "TBI":"Tỉnh Thái Bình","TGI":"Tỉnh Tiền Giang","THO":"Tỉnh Thanh Hóa","TNG":"Tỉnh Thái Nguyên",
    "TNI":"Tỉnh Tây Ninh","TQU":"Tỉnh Tuyên Quang","TVI":"Tỉnh Trà Vinh","VLO":"Tỉnh Vĩnh Long",
    "VPH":"Tỉnh Vĩnh Phúc",
}

def get_region(code):
    parts = code.split(".")
    return REGION_MAP.get(parts[1], parts[1]) if len(parts) >= 2 else ""
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
        headers = {"Authorization": f"token {TOKEN}",
                   "Accept": "application/vnd.github.v3+json"}
        req = urllib.request.Request(
            f"https://api.github.com/gists/{GIST_ID}", headers=headers)
        g = json.loads(urllib.request.urlopen(req, timeout=10).read())
        files = g.get("files", {})

        def parse(fname):
            f = files.get(fname, {})
            if f.get("truncated"):
                raw = urllib.request.Request(f["raw_url"], headers=headers)
                return json.loads(urllib.request.urlopen(raw, timeout=15).read())
            c = f.get("content", "")
            return json.loads(c) if c else {}

        return parse(FILENAME), parse(INV_FILENAME), None
    except Exception as e:
        saleout = json.loads(LOCAL_DATA.read_text(encoding="utf-8")) if LOCAL_DATA.exists() else {}
        inv     = json.loads(LOCAL_INV.read_text(encoding="utf-8"))  if LOCAL_INV.exists()  else {}
        if saleout:
            return saleout, inv, None
        return {}, {}, str(e)

records, inv_records, load_error = load_data()
if load_error:
    st.error(f"데이터 로드 실패: {load_error}")

# ── 쿼리 파라미터로 상태 관리 ─────────────────────────────────────────
def get_state():
    p = st.query_params
    return {
        "page":         p.get("p", "home"),
        "selected_asm": p.get("asm", None),
        "selected_npp": p.get("npp", None),
        "month":        int(p.get("m", 8)),
        "src":          p.get("src", "asm"),
    }

def set_state(page, **kwargs):
    params = {"p": page}
    if "asm" in kwargs:     params["asm"] = kwargs["asm"]
    if "npp" in kwargs:     params["npp"] = kwargs["npp"]
    if "month" in kwargs:   params["m"] = str(kwargs["month"])
    st.query_params.update(params)
    st.rerun()

state = get_state()

# ── 유틸 ────────────────────────────────────────────────────────────
def fmt(n):
    return f"{n/1_000_000:.2f}Tr"

def fmt_ty(n):
    return f"{n/1_000_000_000:.2f}Tỷ"

def fmt_inv(n):
    if n >= 1_000_000_000:
        return fmt_ty(n)
    return fmt(n)

def link(href, cls, content):
    return f'<a href="{href}" target="_self" class="{cls}">{content}</a>'

def card_href(page, **kwargs):
    params = f"p={page}"
    for k, v in kwargs.items():
        params += f"&{k}={v}"
    return f"?{params}"

def back_button(label, page, **kwargs):
    params = {"p": page}
    if "asm"   in kwargs: params["asm"] = kwargs["asm"]
    if "npp"   in kwargs: params["npp"] = kwargs["npp"]
    if "month" in kwargs: params["m"]   = str(kwargs["month"])
    query = "&".join(f"{k}={v}" for k, v in params.items())
    month = kwargs.get("month", state["month"])
    st.markdown(
        f'<a href="?{query}" target="_self" class="nav-back">← {label}</a>'
        f'<a href="?p=home&m={month}" target="_self" class="nav-home">🏠 홈</a>',
        unsafe_allow_html=True,
    )

def month_selector(current_month):
    available = sorted([int(k) for k in records.keys() if k.isdigit()])
    if not available:
        return None
    idx = available.index(current_month) if current_month in available else len(available)-1
    m = st.selectbox("월", available, index=idx, format_func=lambda x: f"{x}월", key="month_sel")
    if m != current_month:
        new_params = dict(st.query_params)
        new_params["m"] = str(m)
        st.query_params.update(new_params)
        st.rerun()
    return m

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

# ── 페이지 함수들 ────────────────────────────────────────────────────

def page_home():
    st.markdown("### 📊 엔젤베트남 영업 통합관리")
    st.markdown("---")
    month = state["month"]
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<a href="{card_href('sales_asm', m=month)}" target="_self" class="home-card">
          <div class="home-icon">🗂️</div>
          <div class="home-title">NPP 통합관리</div>
          <div class="home-desc">세일즈맨 SKU별 실적 및 월별 추이</div>
        </a>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<a href="{card_href('asm_meetings')}" target="_self" class="home-card">
          <div class="home-icon">📋</div>
          <div class="home-title">ASM 회의보고</div>
          <div class="home-desc">ASM별 회의 보고 내용 확인</div>
        </a>""", unsafe_allow_html=True)


def page_npp_inventory():
    back_button("홈으로", "home")
    st.markdown("## 🏪 NPP별 재고관리")
    st.info("재고 데이터를 업로드하면 활성화됩니다.")


def _asm_grid(page_target, btn_label, month):
    month_data = records.get(str(month), {})
    asm_totals = {}
    for code, d in month_data.items():
        asm = d.get("asm", "기타")
        asm_totals.setdefault(asm, {"total": 0, "npps": 0, "salesmen": set()})
        asm_totals[asm]["total"] += d.get("total", 0)
        asm_totals[asm]["npps"] += 1
        asm_totals[asm]["salesmen"].update(d.get("salesmen", {}).keys())

    sorted_asms = sorted(asm_totals.items(), key=lambda x: -x[1]["total"])
    COLS = 4
    rows = [sorted_asms[i:i+COLS] for i in range(0, len(sorted_asms), COLS)]
    for row in rows:
        cols = st.columns(COLS)
        for col, (asm_code, data) in zip(cols, row):
            full_name = ASM_FULL.get(asm_code, asm_code)
            href = card_href(page_target, asm=asm_code, m=month)
            with col:
                st.markdown(f"""<a href="{href}" target="_self" class="asm-card">
                  <div class="asm-name">{full_name}</div>
                  <div class="asm-sub">NPP {data['npps']}개 · 세일즈맨 {len(data['salesmen'])}명</div>
                  <div class="asm-amt">{fmt_ty(data['total'])}</div>
                </a>""", unsafe_allow_html=True)


def page_asm_saleout():
    back_button("홈으로", "home")
    st.markdown("## 📈 ASM별 세일아웃관리")
    col_m, _ = st.columns([2, 6])
    with col_m:
        month = month_selector(state["month"])
    if not month: return
    st.markdown("---")
    _asm_grid("asm_npp_list", "상세보기", month)


def page_asm_npp_list():
    asm_code = state["selected_asm"]
    month    = state["month"]
    back_button("ASM 목록으로", "asm_saleout", month=month)
    full_name = ASM_FULL.get(asm_code, asm_code)
    col_m, _ = st.columns([2, 6])
    with col_m:
        month = month_selector(month)
    if not month: return

    month_data = records.get(str(month), {})
    filtered = {k: v for k, v in month_data.items() if v.get("asm") == asm_code}
    total = sum(d["total"] for d in filtered.values())

    st.markdown(f"### {full_name}")
    k1, k2 = st.columns(2)
    k1.metric("NPP 수", f"{len(filtered)}개")
    k2.metric(f"{month}월 합계", fmt(total))
    st.markdown("---")

    sorted_npps = sorted(filtered.items(), key=lambda x: -x[1]["total"])
    COLS = 4
    for row in [sorted_npps[i:i+COLS] for i in range(0, len(sorted_npps), COLS)]:
        cols = st.columns(COLS)
        for col, (code, d) in zip(cols, row):
            name_short = d["name"][:38] + ("…" if len(d["name"]) > 38 else "")
            href_so  = card_href("sales_npp", npp=code, asm=asm_code, m=month)
            href_inv = card_href("npp_stock",  npp=code, asm=asm_code, m=month, src="asm")
            npp_inv_amt = sum(
                s.get("amt", 0)
                for s in inv_records.get(str(month), {}).get(code, {}).values()
            )
            inv_str = fmt_inv(npp_inv_amt) if npp_inv_amt > 0 else "-"
            saleout_total = d["total"]
            if npp_inv_amt > 0 and saleout_total > 0:
                months_val = npp_inv_amt / saleout_total
                months_str = f"{months_val:.1f}개월"
                months_cls = "npp-half-months-warn" if months_val > 6 else "npp-half-months"
            elif npp_inv_amt > 0:
                months_str = "∞"
                months_cls = "npp-half-months-warn"
            else:
                months_str = ""
                months_cls = "npp-half-months"
            with col:
                st.markdown(f"""<div class="npp-card-wrap">
                  <div class="npp-card-hdr">
                    <div class="npp-title">{code} · {get_region(code) or d.get("province")}</div>
                    <div class="npp-name">{name_short}</div>
                  </div>
                  <div class="npp-card-body">
                    <a href="{href_so}" target="_self" class="npp-half npp-half-left">
                      <div class="npp-half-lbl">Sale out</div>
                      <div class="npp-half-amt">{fmt_inv(d["total"])}</div>
                    </a>
                    <a href="{href_inv}" target="_self" class="npp-half">
                      <div class="npp-half-lbl">재고금액</div>
                      <div class="npp-half-amt npp-half-inv">{inv_str}</div>
                      <div class="{months_cls}">{months_str}</div>
                    </a>
                  </div>
                </div>""", unsafe_allow_html=True)


def page_asm_meetings():
    back_button("홈으로", "home")
    st.markdown("## 📋 ASM 회의보고")
    st.markdown("---")
    st.info("준비 중입니다. 데이터 파일 수신 후 업데이트될 예정입니다.")


def page_sales_asm():
    back_button("홈으로", "home")
    st.markdown("## 🗂️ ASM 세일아웃")
    col_m, _ = st.columns([2, 6])
    with col_m:
        month = month_selector(state["month"])
    if not month: return
    st.markdown("---")
    _asm_grid("sales_npp_list", "ASM 선택", month)


def page_sales_npp_list():
    asm_code = state["selected_asm"]
    month    = state["month"]
    back_button("ASM 목록으로", "sales_asm", month=month)
    full_name = ASM_FULL.get(asm_code, asm_code)
    col_m, _ = st.columns([2, 6])
    with col_m:
        month = month_selector(month)
    if not month: return

    month_data = records.get(str(month), {})
    filtered = {k: v for k, v in month_data.items() if v.get("asm") == asm_code}

    st.markdown(f"### {full_name} 담당 NPP")
    st.markdown("---")

    sorted_npps = sorted(filtered.items(), key=lambda x: -x[1]["total"])
    COLS = 4
    for row in [sorted_npps[i:i+COLS] for i in range(0, len(sorted_npps), COLS)]:
        cols = st.columns(COLS)
        for col, (code, d) in zip(cols, row):
            name_short = d["name"][:38] + ("…" if len(d["name"]) > 38 else "")
            href_so  = card_href("sales_npp", npp=code, asm=asm_code, m=month)
            href_inv = card_href("npp_stock",  npp=code, asm=asm_code, m=month, src="sales")
            npp_inv_amt = sum(
                s.get("amt", 0)
                for s in inv_records.get(str(month), {}).get(code, {}).values()
            )
            inv_str = fmt_inv(npp_inv_amt) if npp_inv_amt > 0 else "-"
            saleout_total = d["total"]
            if npp_inv_amt > 0 and saleout_total > 0:
                months_val = npp_inv_amt / saleout_total
                months_str = f"{months_val:.1f}개월"
                months_cls = "npp-half-months-warn" if months_val > 6 else "npp-half-months"
            elif npp_inv_amt > 0:
                months_str = "∞"
                months_cls = "npp-half-months-warn"
            else:
                months_str = ""
                months_cls = "npp-half-months"
            with col:
                st.markdown(f"""<div class="npp-card-wrap">
                  <div class="npp-card-hdr">
                    <div class="npp-title">{code} · {get_region(code) or d.get("province")}</div>
                    <div class="npp-name">{name_short}</div>
                  </div>
                  <div class="npp-card-body">
                    <a href="{href_so}" target="_self" class="npp-half npp-half-left">
                      <div class="npp-half-lbl">Sale out</div>
                      <div class="npp-half-amt">{fmt_inv(d["total"])}</div>
                    </a>
                    <a href="{href_inv}" target="_self" class="npp-half">
                      <div class="npp-half-lbl">재고금액</div>
                      <div class="npp-half-amt npp-half-inv">{inv_str}</div>
                      <div class="{months_cls}">{months_str}</div>
                    </a>
                  </div>
                </div>""", unsafe_allow_html=True)


def page_sales_npp():
    asm_code = state["selected_asm"]
    month    = state["month"]
    prev_page = "sales_npp_list" if asm_code else "sales_asm"
    prev_label = "NPP 목록으로" if asm_code else "ASM 목록으로"
    back_button(prev_label, prev_page, asm=asm_code, month=month)

    code = state["selected_npp"]
    col_m, _ = st.columns([2, 6])
    with col_m:
        month = month_selector(month)
    if not month: return

    month_data = records.get(str(month), {})
    npp = month_data.get(code)
    if not npp:
        st.warning(f"{month}월 데이터가 없습니다."); return

    asm = npp.get("asm", "")
    asm_name = ASM_FULL.get(asm, asm)
    province = get_region(code) or npp.get("province")
    st.markdown(f"### {npp['name']}  <small style='color:#888;font-size:0.75rem;font-weight:400;'>{province}</small>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("ASM", asm_name)
    c2.metric(f"{month}월 합계", fmt(npp["total"]))
    c3.metric("세일즈맨 수", len(npp.get("salesmen", {})))

    st.markdown("---")
    sku_totals = {sku: 0 for sku in SKU_LIST}
    for sa_data in npp.get("salesmen", {}).values():
        for sku, amt in sa_data.get("skus", {}).items():
            if sku in sku_totals:
                sku_totals[sku] += amt
    cols = st.columns(len(SKU_LIST))
    for i, sku in enumerate(SKU_LIST):
        cols[i].metric(sku, fmt(sku_totals[sku]))

    st.markdown("---")
    st.markdown("### 세일즈맨별 실적")
    salesmen = npp.get("salesmen", {})
    sorted_sa = sorted(salesmen.items(), key=lambda x: -x[1].get("total", 0))

    SKU_SHORT = {
        "BS VÀ HMP CŨ": "BS VÀ HMP CŨ",
        "GIẶT XẢ":      "GIẶT XẢ",
        "PPSU":          "PPSU",
        "KHĂN ƯỚT":     "KHĂN ƯỚT",
        "SỮA TẮM":      "SỮA TẮM",
    }

    col_widths = [2.5] + [1.0] * month + [1.5]
    header = st.columns(col_widths)
    header[0].markdown("**세일즈맨**")
    for i in range(month):
        header[i + 1].markdown(f"**{i+1}월**")
    header[-1].markdown("**추이**")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    for sa_name, sa_data in sorted_sa:
        skus = sa_data.get("skus", {})
        monthly = []
        for m in MONTHS:
            m_npp = records.get(str(m), {}).get(code, {})
            m_sa  = m_npp.get("salesmen", {}).get(sa_name, {})
            monthly.append(m_sa.get("total", 0))

        active_skus = [
            SKU_SHORT[sku] for sku in SKU_LIST
            if skus.get(sku, 0) > 0 and not (sku == "GIẶT XẢ" and month >= 8)
        ]
        sku_str = ", ".join(active_skus)

        row = st.columns(col_widths)
        display_name = sa_name.split("(NPP")[0].replace("Sale ", "").strip()
        name_html = f"**{display_name}** &nbsp;({sku_str})" if sku_str else f"**{display_name}**"
        row[0].markdown(name_html, unsafe_allow_html=True)
        for i in range(month):
            row[i + 1].markdown(fmt(monthly[i]))
        svg = sparkline_svg(monthly[:month], width=140, height=36, color="#4A9EFF")
        row[-1].markdown(svg, unsafe_allow_html=True)


def page_npp_stock():
    asm_code = state["selected_asm"]
    month    = state["month"]
    src      = state.get("src", "asm")
    code     = state["selected_npp"]

    if src == "sales":
        back_button("NPP 목록으로", "sales_npp_list", asm=asm_code, month=month)
    else:
        back_button("NPP 목록으로", "asm_npp_list", asm=asm_code, month=month)

    month_data = records.get(str(month), {})
    npp = month_data.get(code, {})
    name     = npp.get("name", code)
    province = get_region(code) or npp.get("province")

    st.markdown(
        f"### {name}  <small style='color:#888;font-size:0.75rem;font-weight:400;'>{province}</small>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='breadcrumb'>{code}</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"#### 📦 {month}월 SKU별 재고 현황")

    npp_inv = inv_records.get(str(month), {}).get(code, {})
    if not npp_inv:
        st.warning(f"{month}월 재고 데이터가 없습니다. update_integrated.py를 실행해주세요.")
        return

    hdr = st.columns([2.2, 1.1, 1.4, 1.5])
    hdr[0].markdown("**SKU**")
    hdr[1].markdown("**재고수량**")
    hdr[2].markdown("**재고금액**")
    hdr[3].markdown("**예상사용월수**")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    total_inv_amt = 0
    for sku in SKU_LIST:
        sku_data = npp_inv.get(sku, {})
        qty = sku_data.get("qty", 0)
        amt = sku_data.get("amt", 0)
        total_inv_amt += amt

        # 월평균 세일아웃 계산 (해당 월까지의 비영 월 평균)
        monthly_sales = []
        for m in range(1, month + 1):
            m_npp = records.get(str(m), {}).get(code, {})
            m_sku_total = sum(
                sa.get("skus", {}).get(sku, 0)
                for sa in m_npp.get("salesmen", {}).values()
            )
            if m_sku_total > 0:
                monthly_sales.append(m_sku_total)

        avg_monthly = sum(monthly_sales) / len(monthly_sales) if monthly_sales else 0

        if amt <= 0:
            months_str = "—"
            months_color = ""
        elif avg_monthly <= 0:
            months_str = "∞"
            months_color = "color:#ff7875;font-weight:600;"
        else:
            ms = amt / avg_monthly
            months_str = f"{ms:.1f}개월"
            months_color = "color:#ff7875;font-weight:600;" if ms > 6 else ""

        row = st.columns([2.2, 1.1, 1.4, 1.5])
        row[0].markdown(f"{SKU_ICONS.get(sku, '')} {sku}")
        row[1].markdown(f"{int(qty):,}" if qty > 0 else "—")
        row[2].markdown(fmt_inv(amt) if amt > 0 else "—")
        if months_color:
            row[3].markdown(f"<span style='{months_color}'>{months_str}</span>", unsafe_allow_html=True)
        else:
            row[3].markdown(months_str)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    tot_col = st.columns([2.2, 1.1, 1.4, 1.5])
    tot_col[0].markdown("**합계**")
    tot_col[1].markdown("")
    tot_col[2].markdown(f"**{fmt_inv(total_inv_amt)}**")
    tot_col[3].markdown("")


# ── 라우팅 ───────────────────────────────────────────────────────────
PAGE_MAP = {
    "home":           page_home,
    "npp_inventory":  page_npp_inventory,
    "asm_saleout":    page_asm_saleout,
    "asm_npp_list":   page_asm_npp_list,
    "asm_meetings":   page_asm_meetings,
    "sales_asm":      page_sales_asm,
    "sales_npp_list": page_sales_npp_list,
    "sales_npp":      page_sales_npp,
    "npp_stock":      page_npp_stock,
}
PAGE_MAP.get(state["page"], page_home)()
