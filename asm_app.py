# -*- coding: utf-8 -*-
"""ASM 전용 앱 — 로그인 필수, 본인 NPP만 표시"""
import streamlit as st
import json, urllib.request, hashlib
from pathlib import Path
import plotly.graph_objects as go

st.set_page_config(
    page_title="Angel Vietnam - ASM",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  .block-container { padding-top: 3rem !important; padding-bottom: 5rem; }
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
  .npp-staff { font-size: 0.78rem; color: #aaa; margin-top: 3px; }

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
ASM_PW_FILE  = "asm_passwords.json"
LOCAL_DATA   = Path(__file__).parent / "data" / "integrated_records.json"
LOCAL_INV    = Path(__file__).parent / "data" / "inventory_records.json"

SKU_LIST = ["BS VÀ HMP CŨ", "GIẶT XẢ", "PPSU", "KHĂN ƯỚT", "SỮA TẮM"]
SKU_ICONS = {
    "BS VÀ HMP CŨ": "🍼", "GIẶT XẢ": "👕", "PPSU": "👑",
    "KHĂN ƯỚT": "🧻", "SỮA TẮM": "🛁",
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

ASM_FULL = {
    'NHU':'Nguyễn Văn Như','HAI':'Diệp Thế Hải','VINH':'Nguyễn Văn Vịnh',
    'LAM':'Kiều Phú Lâm','QUOC':'Nguyễn Minh Quốc','TU':'Nguyễn Hữu Bảy Tú',
    'HUNG':'Trần Văn Thanh Hùng','VAN':'Mai Hà Văn','TU,HOI':'Tú, Hoi',
}
MONTHS = list(range(1, 13))

LOGIN_TO_ASM = {
    'NHU':'NHU','HAI':'HAI','VINH':'VINH','LAM':'LAM',
    'QUOC':'QUOC','TU':'TU','HUNG':'HUNG','VAN':'VAN','TUHOI':'TU,HOI',
}

KPP_ALIAS = {'KPP.HPH.0001': 'KPP.HPH.00003'}
def normalize_kpp(code): return KPP_ALIAS.get(code, code)

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
        return (saleout, inv, None) if saleout else ({}, {}, str(e))

@st.cache_data(ttl=60)
def load_asm_passwords():
    try:
        headers = {"Authorization": f"token {TOKEN}",
                   "Accept": "application/vnd.github.v3+json"}
        req = urllib.request.Request(
            f"https://api.github.com/gists/{GIST_ID}", headers=headers)
        g = json.loads(urllib.request.urlopen(req, timeout=10).read())
        f = g.get("files", {}).get(ASM_PW_FILE, {})
        if f.get("truncated"):
            rr = urllib.request.Request(f["raw_url"], headers=headers)
            return json.loads(urllib.request.urlopen(rr, timeout=15).read())
        c = f.get("content", "")
        return json.loads(c) if c else {}
    except Exception:
        return {}

def save_asm_password(login_id, new_hash):
    pws = dict(load_asm_passwords())
    pws[login_id] = new_hash
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }
    payload = json.dumps({
        "files": {ASM_PW_FILE: {"content": json.dumps(pws, ensure_ascii=False)}}
    }).encode()
    req = urllib.request.Request(
        f"https://api.github.com/gists/{GIST_ID}",
        data=payload, headers=headers, method="PATCH")
    urllib.request.urlopen(req, timeout=10)
    load_asm_passwords.clear()

def _hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

records, inv_records, load_error = load_data()
if load_error:
    st.error(f"Lỗi tải dữ liệu: {load_error}")

# ── 쿼리 파라미터로 상태 관리 ─────────────────────────────────────────
def get_state():
    p = st.query_params
    return {
        "page":         p.get("p", "home"),
        "selected_asm": p.get("asm", None),
        "selected_npp": p.get("npp", None),
        "month":        int(p.get("m", 8)),
        "src":          p.get("src", "sales"),
        "sp":           p.get("sp", None),
    }

state = get_state()

# ── 유틸 ────────────────────────────────────────────────────────────
def fmt(n):    return f"{n/1_000_000:.2f}Tr"
def fmt_ty(n): return f"{n/1_000_000_000:.2f}Tỷ"
def fmt_inv(n):
    if n >= 1_000_000_000: return fmt_ty(n)
    return fmt(n)

def get_region(code):
    parts = code.split(".")
    return REGION_MAP.get(parts[1], parts[1]) if len(parts) >= 2 else ""

def nav_to(**kwargs):
    """Streamlit 내부 네비게이션 — 세션 유지"""
    st.query_params.update(kwargs)
    st.rerun()

def back_button(label, page, **kwargs):
    params = {"p": page}
    if "asm"   in kwargs: params["asm"] = kwargs["asm"]
    if "month" in kwargs: params["m"]   = str(kwargs["month"])
    if "sp"    in kwargs: params["sp"]  = kwargs["sp"]
    month = kwargs.get("month", state["month"])
    c1, c2, _ = st.columns([1, 1, 6])
    with c1:
        if st.button(f"← {label}", key=f"back__{page}__{state['page']}"):
            nav_to(**params)
    with c2:
        if st.button("🏠 Trang chủ", key=f"home__{page}__{state['page']}"):
            nav_to(p="home", m=str(month))

def month_selector(current_month):
    available = sorted([int(k) for k in records.keys() if k.isdigit()])
    if not available: return None
    idx = available.index(current_month) if current_month in available else len(available)-1
    m = st.selectbox("Tháng", available, index=idx, format_func=lambda x: f"Tháng {x}", key="month_sel")
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

def quarter_avg_sale(code, month):
    if month <= 3:   ms = list(range(1, month+1))
    elif month <= 6: ms = list(range(4, month+1))
    else:            ms = list(range(7, month+1))
    vals = [records.get(str(m), {}).get(code, {}).get("total", 0) for m in ms]
    total = sum(vals)
    count = sum(1 for v in vals if v > 0)
    return total / len(ms) if count > 0 else 0

def inv_status(code, month, inv_amt):
    if inv_amt <= 0: return "", "npp-half-months", ""
    avg = quarter_avg_sale(code, month)
    if avg <= 0: return "", "npp-half-months", ""
    optimal = avg * 6
    ratio = (inv_amt - optimal) / optimal * 100
    optimal_str = fmt_inv(optimal)
    if ratio > 0: return f"+{ratio:.0f}% 초과", "npp-half-months-warn", optimal_str
    return f"{ratio:.0f}% 부족", "npp-half-months", optimal_str

# ── ASM 인증 함수 ─────────────────────────────────────────────────────
def _asm_login_id():
    return st.session_state.get("asm_login_id", "")

def _asm_code():
    return LOGIN_TO_ASM.get(_asm_login_id(), "")

def _asm_header():
    login_id  = _asm_login_id()
    full_name = ASM_FULL.get(_asm_code(), login_id)
    c1, c2, c3 = st.columns([5, 1, 1])
    with c1:
        st.markdown(
            f"<span style='font-size:0.85rem;color:#888;'>👤 {full_name} ({login_id})</span>",
            unsafe_allow_html=True)
    with c2:
        if st.button("Đổi mật khẩu", key="hdr_chpw", use_container_width=True):
            st.session_state["asm_change_pw"] = True
            st.rerun()
    with c3:
        if st.button("Đăng xuất", key="hdr_logout", use_container_width=True):
            for k in ["asm_login_id", "asm_change_pw"]:
                st.session_state.pop(k, None)
            st.rerun()
    st.markdown("<hr style='margin:4px 0 16px;border-color:rgba(128,128,128,0.15);'>",
                unsafe_allow_html=True)

def page_login():
    st.markdown("## 🔐 Đăng nhập ASM")
    st.markdown("---")
    _, col, _ = st.columns([1, 2, 1])
    with col:
        login_id = st.text_input("Tài khoản", key="login_id_input").strip().upper()
        password = st.text_input("Mật khẩu", type="password", key="login_pw_input")
        if st.button("Đăng nhập", use_container_width=True, key="login_btn"):
            if login_id not in LOGIN_TO_ASM:
                st.error("Tài khoản không tồn tại.")
            else:
                pws = load_asm_passwords()
                if pws.get(login_id) == _hash_pw(password):
                    st.session_state["asm_login_id"] = login_id
                    st.rerun()
                else:
                    st.error("Mật khẩu không đúng.")

def page_change_password():
    login_id = _asm_login_id()
    st.markdown("#### 🔑 Đổi mật khẩu")
    st.markdown("---")
    _, col, _ = st.columns([1, 2, 1])
    with col:
        cur_pw  = st.text_input("Mật khẩu hiện tại", type="password", key="cur_pw")
        new_pw  = st.text_input("Mật khẩu mới (tối thiểu 6 ký tự)", type="password", key="new_pw")
        new_pw2 = st.text_input("Xác nhận mật khẩu mới", type="password", key="new_pw2")
        b1, b2  = st.columns(2)
        with b1:
            if st.button("Hủy", use_container_width=True, key="cancel_pw_btn"):
                st.session_state.pop("asm_change_pw", None)
                st.rerun()
        with b2:
            if st.button("Xác nhận", use_container_width=True, key="change_pw_btn"):
                pws = load_asm_passwords()
                if pws.get(login_id) != _hash_pw(cur_pw):
                    st.error("Mật khẩu hiện tại không đúng.")
                elif new_pw != new_pw2:
                    st.error("Mật khẩu mới không khớp.")
                elif len(new_pw) < 6:
                    st.error("Mật khẩu phải có ít nhất 6 ký tự.")
                else:
                    try:
                        save_asm_password(login_id, _hash_pw(new_pw))
                        st.success("Đổi mật khẩu thành công.")
                        st.session_state.pop("asm_change_pw", None)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lưu thất bại: {e}")

# ── 페이지 함수 ──────────────────────────────────────────────────────
def page_home():
    st.markdown("### 📊 Angel Vietnam - Quản lý NPP")
    st.markdown("---")
    month = state["month"]
    col, _ = st.columns([1, 1])
    with col:
        st.markdown("""<div class="home-card" style="cursor:default;">
          <div class="home-icon">🗂️</div>
          <div class="home-title">Quản lý NPP</div>
          <div class="home-desc">Doanh số theo SKU và xu hướng hàng tháng</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Vào xem →", key="home_npp_btn", use_container_width=True):
            nav_to(p="npp_list", m=str(month))


def page_npp_list():
    """로그인 ASM의 NPP 목록"""
    asm_code = _asm_code()
    month    = state["month"]
    back_button("Trang chủ", "home", month=month)
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

    st.markdown(f"### NPP phụ trách của {full_name}")
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
            npp_inv_amt = sum(
                s.get("amt", 0) for sk, s in inv_month.get(code, {}).items()
                if not sk.startswith("_")
            )
            inv_str = fmt_inv(npp_inv_amt) if npp_inv_amt > 0 else "-"
            months_str, months_cls, optimal_str = inv_status(code, month, npp_inv_amt)
            wrap_cls = "npp-card-wrap" + (" npp-no-so" if not has_so else "")
            so_display = fmt_inv(saleout_total) if has_so else "Không có"
            so_badge   = "" if has_so else '<div class="npp-no-so-badge">Không có sale out</div>'
            province   = get_region(code) or d.get("_province") or d.get("province", "")
            current_staff = len(d.get("salesmen", {})) if has_so else 0
            planned_staff = inv_month.get(code, {}).get("_planned_staff")
            staff_str = (f"{current_staff}/{planned_staff}" if planned_staff
                         else str(current_staff) if current_staff else "")
            staff_html = f'<div class="npp-staff">👤 {staff_str}</div>' if staff_str else ""
            inv_opt = (f"<span style='font-size:0.78rem;color:#888;font-weight:400;'> ({optimal_str})</span>"
                       if optimal_str else "")
            with col:
                st.markdown(
                    f'<div class="{wrap_cls}" style="cursor:default;">'
                    f'<div class="npp-card-hdr">'
                    f'<div class="npp-title">{code} · {province}</div>'
                    f'<div class="npp-name">{name_short}</div>'
                    f'{staff_html}'
                    f'{so_badge}'
                    f'</div>'
                    f'<div class="npp-card-body">'
                    f'<div class="npp-half npp-half-left" style="cursor:default;">'
                    f'<div class="npp-half-lbl">Sale out</div>'
                    f'<div class="npp-half-amt">{so_display}</div>'
                    f'</div>'
                    f'<div class="npp-half" style="cursor:default;">'
                    f'<div class="npp-half-lbl">Tồn kho</div>'
                    f'<div class="npp-half-amt npp-half-inv">{inv_str}{inv_opt}</div>'
                    f'<div class="{months_cls}">{months_str}</div>'
                    f'</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("📊 Doanh số", key=f"so_{code}", use_container_width=True):
                        nav_to(p="npp_detail", npp=code, asm=asm_code, m=str(month))
                with b2:
                    if st.button("📦 Tồn kho", key=f"inv_{code}", use_container_width=True):
                        nav_to(p="npp_stock", npp=code, asm=asm_code, m=str(month))


def page_npp_detail():
    asm_code = state["selected_asm"] or _asm_code()
    month    = state["month"]
    back_button("Danh sách NPP", "npp_list", asm=asm_code, month=month)

    code = state["selected_npp"]
    col_m, _ = st.columns([2, 6])
    with col_m:
        month = month_selector(month)
    if not month: return

    month_data = records.get(str(month), {})
    npp        = month_data.get(code)
    inv_meta   = inv_records.get(str(month), {}).get(code, {})

    if not npp and not inv_meta:
        st.warning(f"Không có dữ liệu tháng {month}."); return

    if npp:
        asm      = npp.get("asm", "")
        name_disp = npp["name"]
        province = get_region(code) or npp.get("province", "")
    else:
        asm      = inv_meta.get("_asm", "")
        name_disp = inv_meta.get("_name", code)
        province = get_region(code) or inv_meta.get("_province", "")

    asm_name = ASM_FULL.get(asm, asm)
    st.markdown(f"### {name_disp}  <small style='color:#888;font-size:0.75rem;font-weight:400;'>{province}</small>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("ASM", asm_name)
    c2.metric(f"Tổng tháng {month}", fmt(npp["total"]) if npp else "Không có sale out")
    current_staff = len(npp.get("salesmen", {})) if npp else 0
    planned_staff = inv_meta.get("_planned_staff")
    staff_disp = f"{current_staff}/{planned_staff}" if planned_staff else str(current_staff)
    c3.metric("Số nhân viên", staff_disp)

    if not npp:
        st.info("NPP này không có dữ liệu sale out trong tháng này.")
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
    st.markdown("### Doanh số theo nhân viên")
    salesmen  = npp.get("salesmen", {})
    sorted_sa = sorted(salesmen.items(), key=lambda x: -x[1].get("total", 0))

    col_widths = [2.5] + [1.0] * month + [1.5]
    header = st.columns(col_widths)
    header[0].markdown("**Nhân viên**")
    for i in range(month):
        header[i + 1].markdown(f"**T{i+1}**")
    header[-1].markdown("**Xu hướng**")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    SKU_SHORT = {
        "BS VÀ HMP CŨ": "BS VÀ HMP CŨ", "GIẶT XẢ": "GIẶT XẢ",
        "PPSU": "PPSU", "KHĂN ƯỚT": "KHĂN ƯỚT", "SỮA TẮM": "SỮA TẮM",
    }
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
                row[i+1].markdown(f"{fmt(amt)}<br><span style='color:{pct_color};font-weight:700;'>{pct:.1f}%</span>", unsafe_allow_html=True)
            else:
                row[i+1].markdown(fmt(amt) if amt else "—")
        svg = sparkline_svg(monthly[:month], width=140, height=36, color="#4A9EFF")
        row[-1].markdown(svg, unsafe_allow_html=True)


def page_npp_stock():
    asm_code = state["selected_asm"] or _asm_code()
    month    = state["month"]
    code     = state["selected_npp"]
    back_button("Danh sách NPP", "npp_list", asm=asm_code, month=month)

    month_data = records.get(str(month), {})
    npp        = month_data.get(code, {})
    inv_meta   = inv_records.get(str(month), {}).get(code, {})
    name       = npp.get("name") or inv_meta.get("_name") or code
    province   = get_region(code) or npp.get("province") or inv_meta.get("_province", "")

    st.markdown(
        f"### {name}  <small style='color:#888;font-size:0.75rem;font-weight:400;'>{province}</small>",
        unsafe_allow_html=True)
    st.markdown(f"<div class='breadcrumb'>{code}</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"#### 📦 Tình trạng tồn kho theo SKU - Tháng {month}")

    npp_inv = inv_records.get(str(month), {}).get(code, {})
    if not npp_inv:
        st.warning(f"Không có dữ liệu tồn kho tháng {month}.")
        return

    hdr = st.columns([2.2, 1.1, 1.4, 1.5])
    hdr[0].markdown("**SKU**"); hdr[1].markdown("**Số lượng**")
    hdr[2].markdown("**Giá trị tồn kho**"); hdr[3].markdown("**Tháng sử dụng dự kiến**")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    total_inv_amt = 0
    for sku in SKU_LIST:
        sku_data = npp_inv.get(sku, {})
        qty = sku_data.get("qty", 0)
        amt = sku_data.get("amt", 0)
        total_inv_amt += amt

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
            months_str = "—"; months_color = ""
        elif avg_monthly <= 0:
            months_str = "∞"; months_color = "color:#ff7875;font-weight:600;"
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
    tot_col[0].markdown("**Tổng**"); tot_col[2].markdown(f"**{fmt_inv(total_inv_amt)}**")


# ── 라우팅 ───────────────────────────────────────────────────────────
if not _asm_login_id():
    page_login()
elif st.session_state.get("asm_change_pw"):
    _asm_header()
    page_change_password()
else:
    _asm_header()
    PAGE_MAP = {
        "home":       page_home,
        "npp_list":   page_npp_list,
        "npp_detail": page_npp_detail,
        "npp_stock":  page_npp_stock,
    }
    PAGE_MAP.get(state["page"], page_home)()
