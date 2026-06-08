import html
import json
import math
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st


TOPICS = [
    ("線性迴歸", "Linear Regression", "監督式學習", "以直線描述特徵與連續目標值的關係。", "房價與銷售額預測"),
    ("邏輯迴歸", "Logistic Regression", "監督式學習", "將線性輸出轉換為分類機率。", "垃圾郵件與風險分類"),
    ("決策樹", "Decision Tree", "監督式學習", "使用條件判斷形成容易閱讀的樹狀規則。", "信用判斷與規則分類"),
    ("隨機森林", "Random Forest", "集成學習", "整合多棵隨機決策樹提升穩定度。", "表格資料與特徵重要度"),
    ("支援向量機", "Support Vector Machine", "監督式學習", "尋找類別之間間隔最大的決策邊界。", "文字與高維資料分類"),
    ("K 最近鄰", "K-Nearest Neighbors", "監督式學習", "依據距離最近的 K 個樣本進行預測。", "相似推薦與小型分類"),
    ("K 平均分群", "K-Means Clustering", "非監督式學習", "將資料分配到 K 個相近的群組。", "客群分析與資料探索"),
    ("主成分分析", "Principal Component Analysis", "非監督式學習", "降低資料維度並保留主要變異。", "降維與資料視覺化"),
    ("梯度提升", "Gradient Boosting", "集成學習", "逐步加入模型修正前一輪的錯誤。", "表格資料與風險預測"),
    ("神經網路", "Neural Network", "深度學習", "使用多層神經元學習複雜非線性特徵。", "影像、語音與文字"),
]


def clamp(value: float, minimum: int, maximum: int):
    return min(maximum, max(minimum, value))


def build_chart(title: str, complexity: int, regularization: int, training_ratio: int) -> str:
    points = []
    for index in range(24):
        angle = index * 0.72 + len(title) * 0.15
        spread = 42 + complexity * 0.65 - regularization * 0.18
        center_x = 132 if index % 2 == 0 else 258
        center_y = 106 if index % 2 == 0 else 178
        shift = (training_ratio - 65) * (0.9 if index % 3 == 0 else -0.35)
        x = clamp(center_x + math.cos(angle) * spread + shift, 70, 340)
        y = clamp(center_y + math.sin(angle * 1.15) * spread * 0.68, 58, 232)
        color = "#2f6fab" if index % 2 == 0 else "#b7791f"
        points.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{color}" stroke="white" stroke-width="2"/>')

    wiggle = max(4, complexity * 0.32 - regularization * 0.16)
    midpoint = 148 + (regularization - 40) * 0.25
    path = " ".join(
        f"{'M' if index == 0 else 'L'} {72 + index * 33} "
        f"{clamp(midpoint + math.sin(index * 1.18) * wiggle + (index - 4) * 7, 62, 230):.1f}"
        for index in range(9)
    )
    metrics = [
        ("擬合度", clamp(round(48 + complexity * 0.48 - regularization * 0.12), 25, 98)),
        (
            "泛化",
            clamp(round(62 + training_ratio * 0.18 + regularization * 0.16 - abs(complexity - 58) * 0.28), 25, 98),
        ),
        ("穩定度", clamp(round(38 + regularization * 0.42 + training_ratio * 0.08), 25, 98)),
    ]
    bars = "".join(
        f'<text x="390" y="{62 + index * 64}">{label}</text>'
        f'<rect x="390" y="{72 + index * 64}" width="100" height="14" rx="7" fill="#dce4ef"/>'
        f'<rect x="390" y="{72 + index * 64}" width="{value}" height="14" rx="7" fill="#167c68"/>'
        f'<text x="494" y="{84 + index * 64}" font-size="12">{value}%</text>'
        for index, (label, value) in enumerate(metrics)
    )
    return f"""
    <div style="font-family:Arial,sans-serif;color:#1b1f2a">
      <div style="font-weight:700;margin-bottom:8px">{html.escape(title)}</div>
      <svg viewBox="0 0 530 285" style="width:100%;background:#f7faff;border:1px solid #d9e0e8;border-radius:10px">
        <rect x="38" y="22" width="330" height="238" rx="10" fill="white" stroke="#dce4ef"/>
        <line x1="58" y1="240" x2="348" y2="240" stroke="#9fb0c1" stroke-width="2"/>
        <line x1="58" y1="48" x2="58" y2="240" stroke="#9fb0c1" stroke-width="2"/>
        <path d="{path}" fill="none" stroke="#167c68" stroke-width="4" stroke-linecap="round"/>
        {''.join(points)}
        {bars}
      </svg>
    </div>
    """


def get_secret(name: str) -> str:
    try:
        return str(st.secrets.get(name, ""))
    except FileNotFoundError:
        return os.getenv(name, "")


def ask_ai(topic: dict, question: str) -> str:
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        return "尚未設定 OPENAI_API_KEY。請到 Streamlit App Settings → Secrets 加入金鑰。"

    payload = {
        "model": get_secret("OPENAI_MODEL") or "gpt-5.5",
        "instructions": "你是友善的機器學習助教，請使用繁體中文清楚、精簡地回答。",
        "input": f"課程：{topic['name']} ({topic['english']})\n摘要：{topic['summary']}\n問題：{question}",
    }
    request = Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=60) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        return f"AI 服務回傳錯誤：HTTP {error.code}"
    except (URLError, TimeoutError, json.JSONDecodeError):
        return "目前無法連線至 AI 服務，請稍後再試。"

    texts = [
        content.get("text", "")
        for output in body.get("output", [])
        for content in output.get("content", [])
        if content.get("type") == "output_text"
    ]
    return "\n".join(texts).strip() or "AI 服務沒有回傳內容。"


def topic_record(item: tuple[str, str, str, str, str]) -> dict:
    name, english, family, summary, use = item
    return {"name": name, "english": english, "family": family, "summary": summary, "use": use}


st.set_page_config(page_title="十大機器學習演算法互動平台", page_icon="📊", layout="wide")
st.title("十大機器學習演算法互動平台")
st.caption("互動調參、視覺化與 AI 問答整合版")

topics = [topic_record(item) for item in TOPICS]
with st.sidebar:
    st.header("選擇課程")
    family = st.selectbox("演算法類型", ["全部"] + sorted({item["family"] for item in topics}))
    query = st.text_input("搜尋", placeholder="輸入名稱或關鍵字")

filtered = [
    item
    for item in topics
    if (family == "全部" or item["family"] == family)
    and (
        not query
        or query.casefold() in item["name"].casefold()
        or query.casefold() in item["english"].casefold()
        or query.casefold() in item["summary"].casefold()
    )
]
if not filtered:
    st.warning("找不到符合條件的演算法。")
    st.stop()

selected = st.selectbox(
    "目前課程",
    [item["english"] for item in filtered],
    format_func=lambda value: next(f"{item['name']} · {item['english']}" for item in filtered if item["english"] == value),
)
topic = next(item for item in filtered if item["english"] == selected)
st.subheader(f"{topic['name']} · {topic['english']}")
st.info(topic["summary"])

controls, chart = st.columns([0.38, 0.62], gap="large")
with controls:
    st.markdown("### 參數調整")
    complexity = st.slider("模型複雜度", 10, 100, 55)
    regularization = st.slider("正則化強度", 0, 100, 35)
    training_ratio = st.slider("訓練資料比例", 40, 90, 70)
    st.metric("建議使用情境", topic["use"])
with chart:
    st.markdown("### 演算法圖表")
    st.html(build_chart(topic["english"], complexity, regularization, training_ratio))

st.divider()
st.markdown("### AI 學習助理")
st.caption("在 Streamlit Community Cloud 的 App settings → Secrets 設定 OPENAI_API_KEY 後即可使用。")
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
if prompt := st.chat_input(f"詢問關於 {topic['english']} 的問題"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("正在思考..."):
            answer = ask_ai(topic, prompt)
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
