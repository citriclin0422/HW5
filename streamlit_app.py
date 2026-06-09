import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st

from backend.app.topics import TOPICS
from model_visualizations import render_model_visualization


def normalize_difficulty(value: str) -> str:
    if "進" in value or "難" in value:
        return "進階"
    if "中" in value:
        return "中等"
    return "簡單"


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
        "input": f"課程：{topic['title']} ({topic['english']})\n摘要：{topic['summary']}\n問題：{question}",
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


def choose_topic(slug: str):
    st.session_state.active_slug = slug


st.set_page_config(page_title="十大機器學習演算法互動平台", page_icon="📊", layout="wide")

if "active_slug" not in st.session_state:
    st.session_state.active_slug = TOPICS[0]["slug"]
if "completed" not in st.session_state:
    st.session_state.completed = set()
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("十大機器學習演算法互動平台")
st.caption("用互動課程、參數視覺化、AI 問答與小測驗，理解經典機器學習演算法。")

completed_count = len(st.session_state.completed)
stat1, stat2, stat3 = st.columns(3)
stat1.metric("課程總數", len(TOPICS))
stat2.metric("已完成", completed_count)
stat3.metric("學習進度", f"{round(completed_count / len(TOPICS) * 100)}%")
st.progress(completed_count / len(TOPICS))

with st.sidebar:
    st.header("選擇課程")
    query = st.text_input("搜尋", placeholder="輸入名稱或關鍵字")
    family = st.selectbox("演算法類型", ["全部"] + sorted({topic["family"] for topic in TOPICS}))
    difficulty = st.selectbox("難度", ["全部", "簡單", "中等", "進階"])

    filtered = [
        topic
        for topic in TOPICS
        if (family == "全部" or topic["family"] == family)
        and (difficulty == "全部" or normalize_difficulty(topic["difficulty"]) == difficulty)
        and (
            not query
            or query.casefold() in topic["title"].casefold()
            or query.casefold() in topic["english"].casefold()
            or query.casefold() in topic["summary"].casefold()
        )
    ]
    if not filtered:
        st.warning("找不到符合條件的演算法。")
    for topic_item in filtered:
        marker = "✓ " if topic_item["slug"] in st.session_state.completed else ""
        st.button(
            f"{marker}{topic_item['title']} · {topic_item['english']}",
            key=f"topic_{topic_item['slug']}",
            use_container_width=True,
            type="primary" if topic_item["slug"] == st.session_state.active_slug else "secondary",
            on_click=choose_topic,
            args=(topic_item["slug"],),
        )

topic = next((item for item in TOPICS if item["slug"] == st.session_state.active_slug), TOPICS[0])
topic_index = TOPICS.index(topic)

header, navigation = st.columns([0.8, 0.2])
with header:
    st.caption(f"{topic['family']} · {normalize_difficulty(topic['difficulty'])}")
    st.subheader(f"{topic['title']} · {topic['english']}")
with navigation:
    previous, following = st.columns(2)
    previous.button(
        "← 上一課",
        use_container_width=True,
        on_click=choose_topic,
        args=(TOPICS[(topic_index - 1) % len(TOPICS)]["slug"],),
    )
    following.button(
        "下一課 →",
        use_container_width=True,
        on_click=choose_topic,
        args=(TOPICS[(topic_index + 1) % len(TOPICS)]["slug"],),
    )

st.info(topic["summary"])
render_model_visualization(topic)

st.markdown("### 互動教學")
why_tab, steps_tab, strengths_tab, limits_tab = st.tabs(["為什麼重要", "學習步驟", "優點", "限制"])
with why_tab:
    st.write(topic["why"])
    st.success(f"實際例子：{topic['example']}")
with steps_tab:
    for index, step in enumerate(topic["steps"], start=1):
        st.write(f"**{index}.** {step}")
with strengths_tab:
    for item in topic["strengths"]:
        st.write(f"✓ {item}")
with limits_tab:
    for item in topic["limits"]:
        st.write(f"• {item}")

st.markdown("### 課後小測驗")
st.write(topic["quiz"]["question"])
selected_answer = st.radio(
    "選擇答案",
    topic["quiz"]["options"],
    index=None,
    key=f"quiz_{topic['slug']}",
    label_visibility="collapsed",
)
if selected_answer:
    st.session_state.answers[topic["slug"]] = selected_answer
    if selected_answer == topic["quiz"]["answer"]:
        st.success("答對了，觀念很穩。")
    else:
        st.error(f"再想想看，正確答案是：{topic['quiz']['answer']}")

is_completed = topic["slug"] in st.session_state.completed
if st.button("取消完成" if is_completed else "標記完成", type="primary", use_container_width=True):
    if is_completed:
        st.session_state.completed.remove(topic["slug"])
    else:
        st.session_state.completed.add(topic["slug"])
    st.rerun()

st.divider()
st.markdown("### AI 學習助理")
st.caption("在 Streamlit Community Cloud 的 App settings → Secrets 設定 OPENAI_API_KEY 後即可使用。")
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
