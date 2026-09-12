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

  .npp-no-so { border-style: dashed !important; opacity: 0.82; }
  .npp-no-so-badge { font-size: 0.72rem; color: #fa8c16; margin-top: 2px; font-weight: 600; }

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
    'HUNG':'Trần Văn Thanh Hùng','VAN':'Mai Hà Văn','TU,HOI':'Tú, Hoi',
}
MONTHS = list(range(1, 13))

# 코드 변경된 동일 업체 alias (구코드 → 신코드)
KPP_ALIAS = {
    'KPP.HPH.0001': 'KPP.HPH.00003',
}

def normalize_kpp(code):
    return KPP_ALIAS.get(code, code)

# ASM별 NPP 고정 표시 순서 (2026년 7월 재고파일 컬럼 순서 기준 — 변경 금지)
NPP_ORDER = {
    'TU':    ['KPP.HAN.0009','KPP.PTH.0008','KPP.BNI.0005','KPP.BGI.0004',
              'KPP.TQU.00002','KPP.VPH.0002','KPP.TNG.0003','KPP.HGI.0001',
              'KPP.PTH.00009','KPP.LCA.00002'],
    'VINH':  ['KPP.HAN.0010','KPP.QNI.0004','KPP.HPH.0001','KPP.HPH.00003','KPP.HPH.00002',
              'KPP.HYE.0005'],
    'TU,HOI':['KPP.NAN.0006','KPP.NDI.0006','KPP.NBI.00003','KPP.QBI.0002',
              'KPP.HTI.00007','KPP.THO.0005','KPP.THO.00006','KPP.TBI.0004'],
    'LAM':   ['KPP.DNA.0003','KPP.HUE.00006','KPP.QTR.0002','KPP.QNG.00004',
              'KPP.QNA.0002','KPP.BDI.0004','KPP.DLA.00007','KPP.DNA.00004'],
    'HAI':   ['KPP.DLA.0006','KPP.GLA.0001','KPP.DLA.0005','KPP.LDO.0003',
              'KPP.LDO.0006','KPP.LDO.0008','KPP.KHH.00005','KPP.DNO.0004',
              'KPP.KHH.00007','KPP.KHH.00006'],
    'QUOC':  ['KPP.DON.0005','KPP.DON.00008','KPP.BTH.0002','KPP.HCM.00004',
              'KPP.BRV.0004','KPP.DON.00009','KPP.BPH.0005','KPP.BDU.0005',
              'KPP.TNI.00003'],
    'HUNG':  ['KPP.HCM.0003','KPP.TGI.0003','KPP.LAN.0004','KPP.BTR.0003'],
    'NHU':   ['KPP.AGI.0003','KPP.KGI.0004','KPP.DTH.0004','KPP.STR.0015',
              'KPP.TVI.0002','KPP.BLI.0001','KPP.CTH.0006','KPP.CMA.0002',
              'KPP.VLO.0003'],
}

def sort_npps(codes, asm_code):
    """NPP_ORDER 기준으로 정렬. 목록에 없는 코드는 맨 뒤로."""
    order = NPP_ORDER.get(asm_code, [])
    idx = {c: i for i, c in enumerate(order)}
    return sorted(codes, key=lambda c: idx.get(c, len(order)))

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
        "sp":           p.get("sp", None),
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
    if "sp"    in kwargs: params["sp"]  = kwargs["sp"]
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

def quarter_months(month):
    """해당 월이 속한 분기의 1월~해당월까지 월 목록 반환"""
    if month <= 3:
        return list(range(1, month + 1))
    elif month <= 6:
        return list(range(4, month + 1))
    else:
        return list(range(7, month + 1))

def quarter_avg_sale(code, month):
    """분기 평균 sale out 계산"""
    ms = quarter_months(month)
    vals = [records.get(str(m), {}).get(code, {}).get("total", 0) for m in ms]
    total = sum(vals)
    count = sum(1 for v in vals if v > 0)
    if count == 0:
        return 0
    return total / len(ms)

def inv_status(code, month, inv_amt):
    """적정재고 대비 초과율. 적정재고 = 분기 평균 sale out × 6"""
    if inv_amt <= 0:
        return "", "npp-half-months", ""
    avg = quarter_avg_sale(code, month)
    if avg <= 0:
        return "", "npp-half-months", ""
    optimal = avg * 6
    ratio = (inv_amt - optimal) / optimal * 100
    optimal_str = fmt_inv(optimal)
    if ratio > 0:
        return f"+{ratio:.0f}% 초과", "npp-half-months-warn", optimal_str
    else:
        return f"{ratio:.0f}% 부족", "npp-half-months", optimal_str

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
        st.markdown(f"""<a href="{card_href('sa_analysis', m=month)}" target="_self" class="home-card">
          <div class="home-icon">📊</div>
          <div class="home-title">세일즈 분석</div>
          <div class="home-desc">세일즈맨별 매출 달성률 분석</div>
        </a>""", unsafe_allow_html=True)


def page_npp_inventory():
    back_button("홈으로", "home")
    st.markdown("## 🏪 NPP별 재고관리")
    st.info("재고 데이터를 업로드하면 활성화됩니다.")


def _asm_grid(page_target, btn_label, month):
    month_data = records.get(str(month), {})
    inv_month  = inv_records.get(str(month), {})
    asm_totals = {}
    for code, d in month_data.items():
        asm = d.get("asm", "기타")
        asm_totals.setdefault(asm, {"total": 0, "npps": set(), "salesmen": set()})
        asm_totals[asm]["total"] += d.get("total", 0)
        asm_totals[asm]["npps"].add(code)
        asm_totals[asm]["salesmen"].update(d.get("salesmen", {}).keys())

    # 재고에만 있는 NPP(세일아웃 없음)도 ASM 카드 NPP 수에 포함
    for code, inv_d in inv_month.items():
        asm = inv_d.get("_asm")
        if not asm or code in month_data:
            continue
        asm_totals.setdefault(asm, {"total": 0, "npps": set(), "salesmen": set()})
        asm_totals[asm]["npps"].add(code)

    ASM_DISPLAY_ORDER = ['TU','VINH','TU,HOI','LAM','HAI','QUOC','HUNG','NHU','VAN']
    sorted_asms = sorted(asm_totals.items(),
                         key=lambda x: ASM_DISPLAY_ORDER.index(x[0]) if x[0] in ASM_DISPLAY_ORDER else 99)
    COLS = 4
    rows = [sorted_asms[i:i+COLS] for i in range(0, len(sorted_asms), COLS)]
    for ri, row in enumerate(rows):
        if ri > 0:
            st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        cols = st.columns(COLS)
        for col, (asm_code, data) in zip(cols, row):
            full_name = ASM_FULL.get(asm_code, asm_code)
            href = card_href(page_target, asm=asm_code, m=month)
            with col:
                st.markdown(f"""<a href="{href}" target="_self" class="asm-card">
                  <div class="asm-name">{full_name}</div>
                  <div class="asm-sub">NPP {len(data['npps'])}개 · 세일즈맨 {len(data['salesmen'])}명</div>
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
    inv_month  = inv_records.get(str(month), {})
    filtered   = {k: v for k, v in month_data.items() if v.get("asm") == asm_code}
    inv_only   = {k: v for k, v in inv_month.items()
                  if v.get("_asm") == asm_code and k not in filtered}
    total = sum(d["total"] for d in filtered.values())

    st.markdown(f"### {full_name}")
    k1, k2, k3 = st.columns(3)
    k1.metric("NPP 수", f"{len(filtered) + len(inv_only)}개")
    k2.metric(f"{month}월 합계", fmt(total))
    k3.metric("세일아웃 없는 NPP", f"{len(inv_only)}개")
    st.markdown("---")

    all_codes = sort_npps(list(filtered.keys()) + list(inv_only.keys()), asm_code)
    all_npps  = [(k, filtered[k] if k in filtered else inv_only[k], k in filtered) for k in all_codes]
    COLS = 4
    for batch in [all_npps[i:i+COLS] for i in range(0, len(all_npps), COLS)]:
        cols = st.columns(COLS)
        for col, (code, d, has_so) in zip(cols, batch):
            if has_so:
                name = d["name"]
                saleout_total = d["total"]
            else:
                name = d.get("_name", code)
                saleout_total = 0
            name_short = name[:38] + ("…" if len(name) > 38 else "")
            href_so  = card_href("sales_npp", npp=code, asm=asm_code, m=month)
            href_inv = card_href("npp_stock", npp=code, asm=asm_code, m=month, src="asm")
            npp_inv_amt = sum(
                s.get("amt", 0)
                for sk, s in inv_month.get(code, {}).items()
                if not sk.startswith("_")
            )
            inv_str = fmt_inv(npp_inv_amt) if npp_inv_amt > 0 else "-"
            months_str, months_cls, optimal_str = inv_status(code, month, npp_inv_amt)
            wrap_cls = "npp-card-wrap" + (" npp-no-so" if not has_so else "")
            so_display = fmt_inv(saleout_total) if has_so else "없음"
            so_badge = "" if has_so else '<div class="npp-no-so-badge">세일아웃 없음</div>'
            province = get_region(code) or d.get("_province") or d.get("province", "")
            with col:
                st.markdown(
                    f'<div class="{wrap_cls}">'
                    f'<div class="npp-card-hdr">'
                    f'<div class="npp-title">{code} · {province}</div>'
                    f'<div class="npp-name">{name_short}</div>'
                    f'{so_badge}'
                    f'</div>'
                    f'<div class="npp-card-body">'
                    f'<a href="{href_so}" target="_self" class="npp-half npp-half-left">'
                    f'<div class="npp-half-lbl">Sale out</div>'
                    f'<div class="npp-half-amt">{so_display}</div>'
                    f'</a>'
                    f'<a href="{href_inv}" target="_self" class="npp-half">'
                    f'<div class="npp-half-lbl">재고금액</div>'
                    f'<div class="npp-half-amt npp-half-inv">{inv_str}{"<span style=\'font-size:0.78rem;color:#888;font-weight:400;\'> (" + optimal_str + ")</span>" if optimal_str else ""}</div>'
                    f'<div class="{months_cls}">{months_str}</div>'
                    f'</a>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


def page_sa_salesmen():
    """세일즈 분석 > 세일즈맨 서브페이지"""
    back_button("세일즈 분석으로", "sa_analysis")
    st.markdown("## 👤 세일즈맨")

    QUARTERS = {
        "Q1 (1~3월)": [1, 2, 3],
        "Q2 (4~6월)": [4, 5, 6],
        "Q3 (7~8월)": [7, 8],
    }
    cur_month = state["month"]
    default_q = "Q1 (1~3월)"
    for q, ms in QUARTERS.items():
        if cur_month in ms:
            default_q = q
    q_keys = list(QUARTERS.keys())
    col_q, _ = st.columns([2, 6])
    with col_q:
        selected_q = st.selectbox("분기", q_keys, index=q_keys.index(default_q), key="q_sel")
    q_months = QUARTERS[selected_q]
    st.markdown("---")

    sa_map = {}
    for m in q_months:
        m_data = records.get(str(m), {})
        for kpp_code, kpp_data in m_data.items():
            npp_name = kpp_data.get("name", kpp_code)
            asm_code = kpp_data.get("asm", "")
            for sa_name, sa_data in kpp_data.get("salesmen", {}).items():
                key = sa_name[5:] if sa_name.startswith("Sale ") else sa_name
                # 이름에 붙은 SKU 태그 제거 (예: "...Đồng Xoài) KHĂN ƯỚT" → "...Đồng Xoài)")
                if ")" in key:
                    key = key[:key.rfind(")")+1]
                if key not in sa_map:
                    sa_map[key] = {"name": key.split("(NPP")[0].strip(), "total": 0, "target": 0, "months": 0}
                sa_map[key]["npp"]         = npp_name
                sa_map[key]["province"]    = kpp_data.get("province", "")
                sa_map[key]["asm"]         = ASM_FULL.get(asm_code, asm_code)
                sa_map[key]["total"]      += sa_data.get("total", 0)
                sa_map[key]["target"]     += sa_data.get("_target", 0)
                sa_map[key]["months"]     += 1
                if sa_data.get("employee_id") and not sa_map[key].get("employee_id"):
                    sa_map[key]["employee_id"] = sa_data["employee_id"]

    rows = []
    for r in sa_map.values():
        n = r["months"] if r["months"] > 0 else 1
        r["total"]  = r["total"]  / n
        r["target"] = r["target"] / n
        t, tg = r["total"], r["target"]
        r["pct"] = t / tg * 100 if tg > 0 else None
        rows.append(r)

    sort_key = st.session_state.get("sa_sort", "pct")
    col_sort, _ = st.columns([3, 5])
    with col_sort:
        sort_label = "달성률 순" if sort_key == "pct" else "실적 순"
        if st.button(f"정렬: {sort_label} (클릭하여 전환)", key="sa_sort_btn"):
            st.session_state["sa_sort"] = "total" if sort_key == "pct" else "pct"
            st.rerun()

    def sort_rows(rows, key):
        has_target = [r for r in rows if r["pct"] is not None]
        no_target  = [r for r in rows if r["pct"] is None]
        if key == "pct":
            has_target.sort(key=lambda x: -x["pct"])
        else:
            has_target.sort(key=lambda x: -x["total"])
        no_target.sort(key=lambda x: -x["total"])
        return has_target + no_target

    all_rows = sort_rows(rows, sort_key)

    st.markdown(f"**{selected_q} 전체 세일즈맨 {len(all_rows)}명**")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    hdr = st.columns([0.4, 2.0, 2.2, 1.0, 1.0, 1.3, 1.3, 1.1])
    for col, label in zip(hdr, ["**#**","**세일즈맨**","**NPP**","**지역**","**ASM**","**실적**","**타겟**","**달성률**"]):
        col.markdown(label)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    for i, r in enumerate(all_rows, 1):
        pct = r["pct"]
        if pct is not None:
            pct_color = "#10b981" if pct >= 100 else ("#f59e0b" if pct >= 70 else "#ef4444")
            pct_str = f"<span style='color:{pct_color};font-weight:700;'>{pct:.1f}%</span>"
        else:
            pct_str = "<span style='color:#555;'>—</span>"
        row = st.columns([0.4, 2.0, 2.2, 1.0, 1.0, 1.3, 1.3, 1.1])
        row[0].markdown(str(i))
        eid = r.get("employee_id", "")
        eid_str = f" <span style='font-size:0.78rem;color:#666;'>({eid})</span>" if eid else ""
        row[1].markdown(f"{r['name']}{eid_str}", unsafe_allow_html=True)
        row[2].markdown(f"<span style='font-size:0.82rem;color:#888;'>{r.get('npp','')}</span>", unsafe_allow_html=True)
        prov_disp = r.get('province','').replace('Tỉnh ','').replace('Thành phố ','')
        row[3].markdown(f"<span style='font-size:0.82rem;color:#888;'>{prov_disp}</span>", unsafe_allow_html=True)
        row[4].markdown(f"<span style='font-size:0.82rem;'>{r.get('asm','')}</span>", unsafe_allow_html=True)
        row[5].markdown(fmt(r["total"]) if r["total"] else "—")
        row[6].markdown(fmt(r["target"]) if r["target"] else "—")
        row[7].markdown(pct_str, unsafe_allow_html=True)


def page_sa_province():
    back_button("세일즈 분석으로", "sa_analysis")
    st.markdown("## 🗺️ 지역 분석")

    QUARTERS = {"Q1 (1~3월)": [1,2,3], "Q2 (4~6월)": [4,5,6], "Q3 (7~8월)": [7,8]}
    cur_month = state["month"]
    default_q = next((q for q, ms in QUARTERS.items() if cur_month in ms), "Q1 (1~3월)")
    q_keys = list(QUARTERS.keys())
    col_q, _ = st.columns([2, 6])
    with col_q:
        selected_q = st.selectbox("분기", q_keys, index=q_keys.index(default_q), key="prov_q_sel")
    q_months = QUARTERS[selected_q]
    st.markdown("---")

    SKUS = ["BS VÀ HMP CŨ", "PPSU", "KHĂN ƯỚT", "SỮA TẮM"]
    SKU_LABELS = {"BS VÀ HMP CŨ": "BS / HMP", "PPSU": "PPSU", "KHĂN ƯỚT": "KHĂN ƯỚT", "SỮA TẮM": "SỮA TẮM"}

    prov_data = {}
    for m in q_months:
        for kpp_code, kpp_data in records.get(str(m), {}).items():
            prov = kpp_data.get("province", "") or "기타"
            if prov not in prov_data:
                prov_data[prov] = {s: 0 for s in SKUS}
            for sa_data in kpp_data.get("salesmen", {}).values():
                skus = sa_data.get("skus", {})
                for sku in SKUS:
                    prov_data[prov][sku] += skus.get(sku, 0) or 0

    if not prov_data:
        st.info("데이터 없음")
        return

    st.markdown(f"**{selected_q} — SKU별 상위 5개 성**")
    st.markdown("---")

    # 2열 그리드로 SKU 4개 배치
    sku_pairs = [(SKUS[0], SKUS[1]), (SKUS[2], SKUS[3])]
    for sku_left, sku_right in sku_pairs:
        col_l, col_r = st.columns(2)
        for col, sku in [(col_l, sku_left), (col_r, sku_right)]:
            with col:
                ranked = sorted(prov_data.items(), key=lambda x: -x[1][sku])
                top5 = [(prov, d[sku]) for prov, d in ranked if d[sku] > 0][:5]
                max_amt = top5[0][1] if top5 else 1
                st.markdown(f"#### {SKU_LABELS[sku]}")
                if not top5:
                    st.markdown("<span style='color:#555;'>데이터 없음</span>", unsafe_allow_html=True)
                    continue
                for rank, (prov, amt) in enumerate(top5, 1):
                    bar_w = int(amt / max_amt * 100)
                    medal = ["🥇","🥈","🥉","4️⃣","5️⃣"][rank-1]
                    st.markdown(
                        f"<div style='margin-bottom:10px;max-width:630px;'>"
                        f"<div style='display:flex;justify-content:space-between;margin-bottom:3px;'>"
                        f"<span>{medal} {prov}</span>"
                        f"<span style='font-weight:700;'>{fmt_ty(amt)}</span>"
                        f"</div>"
                        f"<div style='background:#222;border-radius:3px;height:6px;'>"
                        f"<div style='background:#4A9EFF;width:{bar_w}%;height:6px;border-radius:3px;'></div>"
                        f"</div></div>",
                        unsafe_allow_html=True
                    )
        st.markdown("---")


def page_sa_analysis():
    sp = state.get("sp")
    if sp == "salesmen":
        page_sa_salesmen()
        return
    if sp == "province":
        page_sa_province()
        return

    back_button("홈으로", "home")
    st.markdown("## 📊 세일즈 분석")
    st.markdown("---")

    m = state["month"]
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<a href="?p=sa_analysis&sp=salesmen&m={m}" target="_self" class="home-card">
  <div class="home-icon">👤</div>
  <div class="home-title">세일즈맨</div>
  <div class="home-desc">분기별 달성률 순위</div>
</a>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<a href="?p=sa_analysis&sp=province&m={m}" target="_self" class="home-card">
  <div class="home-icon">🗺️</div>
  <div class="home-title">지역 분석</div>
  <div class="home-desc">SKU별 상위 5개 성</div>
</a>""", unsafe_allow_html=True)


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
    inv_month  = inv_records.get(str(month), {})
    filtered   = {k: v for k, v in month_data.items() if v.get("asm") == asm_code}
    inv_only   = {k: v for k, v in inv_month.items()
                  if v.get("_asm") == asm_code and k not in filtered}

    st.markdown(f"### {full_name} 담당 NPP")
    st.markdown("---")

    all_codes = sort_npps(list(filtered.keys()) + list(inv_only.keys()), asm_code)
    all_npps  = [(k, filtered[k] if k in filtered else inv_only[k], k in filtered) for k in all_codes]
    COLS = 4
    for batch in [all_npps[i:i+COLS] for i in range(0, len(all_npps), COLS)]:
        cols = st.columns(COLS)
        for col, (code, d, has_so) in zip(cols, batch):
            if has_so:
                name = d["name"]
                saleout_total = d["total"]
            else:
                name = d.get("_name", code)
                saleout_total = 0
            name_short = name[:38] + ("…" if len(name) > 38 else "")
            href_so  = card_href("sales_npp", npp=code, asm=asm_code, m=month)
            href_inv = card_href("npp_stock", npp=code, asm=asm_code, m=month, src="sales")
            npp_inv_amt = sum(
                s.get("amt", 0)
                for sk, s in inv_month.get(code, {}).items()
                if not sk.startswith("_")
            )
            inv_str = fmt_inv(npp_inv_amt) if npp_inv_amt > 0 else "-"
            months_str, months_cls, optimal_str = inv_status(code, month, npp_inv_amt)
            wrap_cls = "npp-card-wrap" + (" npp-no-so" if not has_so else "")
            so_display = fmt_inv(saleout_total) if has_so else "없음"
            so_badge = "" if has_so else '<div class="npp-no-so-badge">세일아웃 없음</div>'
            province = get_region(code) or d.get("_province") or d.get("province", "")
            with col:
                st.markdown(
                    f'<div class="{wrap_cls}">'
                    f'<div class="npp-card-hdr">'
                    f'<div class="npp-title">{code} · {province}</div>'
                    f'<div class="npp-name">{name_short}</div>'
                    f'{so_badge}'
                    f'</div>'
                    f'<div class="npp-card-body">'
                    f'<a href="{href_so}" target="_self" class="npp-half npp-half-left">'
                    f'<div class="npp-half-lbl">Sale out</div>'
                    f'<div class="npp-half-amt">{so_display}</div>'
                    f'</a>'
                    f'<a href="{href_inv}" target="_self" class="npp-half">'
                    f'<div class="npp-half-lbl">재고금액</div>'
                    f'<div class="npp-half-amt npp-half-inv">{inv_str}{"<span style=\'font-size:0.78rem;color:#888;font-weight:400;\'> (" + optimal_str + ")</span>" if optimal_str else ""}</div>'
                    f'<div class="{months_cls}">{months_str}</div>'
                    f'</a>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


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
    inv_meta = inv_records.get(str(month), {}).get(code, {})

    if not npp and not inv_meta:
        st.warning(f"{month}월 데이터가 없습니다."); return

    if npp:
        asm = npp.get("asm", "")
        name_disp = npp["name"]
        province = get_region(code) or npp.get("province", "")
    else:
        asm = inv_meta.get("_asm", "")
        name_disp = inv_meta.get("_name", code)
        province = get_region(code) or inv_meta.get("_province", "")

    asm_name = ASM_FULL.get(asm, asm)
    st.markdown(f"### {name_disp}  <small style='color:#888;font-size:0.75rem;font-weight:400;'>{province}</small>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("ASM", asm_name)
    c2.metric(f"{month}월 합계", fmt(npp["total"]) if npp else "세일아웃 없음")
    current_staff = len(npp.get("salesmen", {})) if npp else 0
    planned_staff = inv_meta.get("_planned_staff")
    staff_disp = f"{current_staff}/{planned_staff}" if planned_staff else str(current_staff)
    c3.metric("세일즈맨 수", staff_disp)

    if not npp:
        st.info("이 NPP는 해당 월에 세일아웃 데이터가 없습니다.")
        return

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
        monthly_target = []
        for m in MONTHS:
            m_npp = records.get(str(m), {}).get(code, {})
            m_sa  = m_npp.get("salesmen", {}).get(sa_name, {})
            monthly.append(m_sa.get("total", 0))
            monthly_target.append(m_sa.get("_target", 0))

        active_skus = [
            SKU_SHORT[sku] for sku in SKU_LIST
            if skus.get(sku, 0) > 0 and not (sku == "GIẶT XẢ" and month >= 8)
        ]
        sku_str = ", ".join(active_skus)

        row = st.columns(col_widths)
        display_name = sa_name.split("(NPP")[0].replace("Sale ", "").strip()
        name_html = f"**{display_name}**" + (f" &nbsp;({sku_str})" if sku_str else "")
        row[0].markdown(name_html, unsafe_allow_html=True)
        for i in range(month):
            amt = monthly[i]
            tgt = monthly_target[i]
            if tgt and tgt > 0:
                pct = amt / tgt * 100
                pct_color = "#10b981" if pct >= 100 else ("#f59e0b" if pct >= 70 else "#ef4444")
                cell_html = f"{fmt(amt)}<br><span style='color:{pct_color};font-weight:700;'>{pct:.1f}%</span>"
                row[i + 1].markdown(cell_html, unsafe_allow_html=True)
            else:
                row[i + 1].markdown(fmt(amt) if amt else "—")
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
    inv_meta = inv_records.get(str(month), {}).get(code, {})
    name     = npp.get("name") or inv_meta.get("_name") or code
    province = get_region(code) or npp.get("province") or inv_meta.get("_province", "")

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

    # ── 재고금액 추이 차트 ────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📈 재고금액 추이")

    inv_series, opt_series, labels = [], [], []
    for m in range(1, month + 1):
        m_inv = inv_records.get(str(m), {}).get(code, {})
        inv_amt_m = sum(v.get("amt", 0) for k, v in m_inv.items()
                        if not k.startswith("_") and isinstance(v, dict))
        inv_series.append(inv_amt_m)
        avg_m = quarter_avg_sale(code, m)
        opt_series.append(avg_m * 6 if avg_m > 0 else None)
        labels.append(f"{m}월")

    n = len(inv_series)
    W, H = 820, 220
    PAD_L, PAD_R, PAD_T, PAD_B = 70, 20, 20, 40
    CW = W - PAD_L - PAD_R
    CH = H - PAD_T - PAD_B

    all_vals = [v for v in inv_series + opt_series if v is not None and v > 0]
    y_max = max(all_vals) * 1.15 if all_vals else 1
    y_min = 0

    def px(i, v):
        x = PAD_L + i * CW / max(n - 1, 1)
        y = PAD_T + CH - (v - y_min) / (y_max - y_min) * CH
        return x, y

    def pts_str(series):
        return " ".join(f"{px(i,v)[0]:.1f},{px(i,v)[1]:.1f}"
                        for i, v in enumerate(series) if v is not None)

    # 적정재고 연속 구간 (None 건너뜀)
    opt_segments, seg = [], []
    for i, v in enumerate(opt_series):
        if v is not None:
            seg.append((i, v))
        else:
            if seg: opt_segments.append(seg)
            seg = []
    if seg: opt_segments.append(seg)

    # Y축 눈금 (4단계)
    y_ticks = [y_min + (y_max - y_min) * k / 4 for k in range(5)]

    svg_lines = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{W}px;">']

    # 격자
    for yv in y_ticks:
        _, yp = px(0, yv)
        svg_lines.append(f'<line x1="{PAD_L}" y1="{yp:.1f}" x2="{W-PAD_R}" y2="{yp:.1f}" stroke="rgba(128,128,128,0.15)" stroke-width="1"/>')

    # Y축 레이블
    for yv in y_ticks:
        _, yp = px(0, yv)
        lbl = fmt_inv(yv) if yv > 0 else "0"
        svg_lines.append(f'<text x="{PAD_L-6}" y="{yp+4:.1f}" text-anchor="end" font-size="11" fill="rgba(128,128,128,0.8)">{lbl}</text>')

    # X축 레이블
    for i, lbl in enumerate(labels):
        xp, _ = px(i, 0)
        svg_lines.append(f'<text x="{xp:.1f}" y="{H-6}" text-anchor="middle" font-size="11" fill="rgba(128,128,128,0.8)">{lbl}</text>')

    # 실재고 영역 채우기
    if n > 1:
        poly_pts = " ".join(f"{px(i,v)[0]:.1f},{px(i,v)[1]:.1f}" for i, v in enumerate(inv_series))
        x0, _ = px(0, 0); xn, _ = px(n-1, 0); _, yb = px(0, 0)
        svg_lines.append(f'<polygon points="{x0:.1f},{PAD_T+CH:.1f} {poly_pts} {xn:.1f},{PAD_T+CH:.1f}" fill="#4A9EFF" opacity="0.1"/>')
        svg_lines.append(f'<polyline points="{poly_pts}" fill="none" stroke="#4A9EFF" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')

    # 적정재고 선 (점선)
    for seg in opt_segments:
        seg_pts = " ".join(f"{px(i,v)[0]:.1f},{px(i,v)[1]:.1f}" for i,v in seg)
        svg_lines.append(f'<polyline points="{seg_pts}" fill="none" stroke="#10b981" stroke-width="2" stroke-dasharray="6 3" stroke-linejoin="round" stroke-linecap="round"/>')

    # 데이터 점
    for i, v in enumerate(inv_series):
        xp, yp = px(i, v)
        svg_lines.append(f'<circle cx="{xp:.1f}" cy="{yp:.1f}" r="3.5" fill="#4A9EFF"/>')
    for i, v in enumerate(opt_series):
        if v is not None:
            xp, yp = px(i, v)
            svg_lines.append(f'<circle cx="{xp:.1f}" cy="{yp:.1f}" r="3" fill="#10b981"/>')

    # 범례
    svg_lines.append(f'<rect x="{PAD_L}" y="{PAD_T}" width="12" height="3" rx="1" fill="#4A9EFF"/>')
    svg_lines.append(f'<text x="{PAD_L+16}" y="{PAD_T+7}" font-size="11" fill="rgba(128,128,128,0.9)">실재고</text>')
    svg_lines.append(f'<line x1="{PAD_L+70}" y1="{PAD_T+1.5}" x2="{PAD_L+82}" y2="{PAD_T+1.5}" stroke="#10b981" stroke-width="2" stroke-dasharray="4 2"/>')
    svg_lines.append(f'<text x="{PAD_L+86}" y="{PAD_T+7}" font-size="11" fill="rgba(128,128,128,0.9)">적정재고</text>')

    svg_lines.append('</svg>')
    st.markdown("".join(svg_lines), unsafe_allow_html=True)


# ── 라우팅 ───────────────────────────────────────────────────────────
PAGE_MAP = {
    "home":           page_home,
    "npp_inventory":  page_npp_inventory,
    "asm_saleout":    page_asm_saleout,
    "asm_npp_list":   page_asm_npp_list,
    "sa_analysis":    page_sa_analysis,
    "sales_asm":      page_sales_asm,
    "sales_npp_list": page_sales_npp_list,
    "sales_npp":      page_sales_npp,
    "npp_stock":      page_npp_stock,
}
PAGE_MAP.get(state["page"], page_home)()
