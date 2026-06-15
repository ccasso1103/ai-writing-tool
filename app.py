import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="AI Writing Studio",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- セッション初期化 ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# --- サイドバー ---
with st.sidebar:
    st.title("✍️ AI Writing\nStudio")
    st.divider()

    api_key = st.text_input(
        "🔑 Gemini APIキー",
        value=st.session_state.api_key,
        type="password",
        placeholder="AIzaSy...",
        help="Google AI Studio（aistudio.google.com）で無料取得できます"
    )
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key

    if st.session_state.api_key:
        if st.button("🔗 接続テスト", use_container_width=True):
            try:
                client = genai.Client(api_key=st.session_state.api_key)
                client.models.generate_content(model="gemini-2.0-flash", contents="hi")
                st.success("接続成功！APIキーは正常です ✓")
            except Exception as e:
                st.error(f"接続失敗：{e}")
    else:
        st.info("↑ APIキーを入力してください\n\n[Google AI Studioで無料取得 →](https://aistudio.google.com/app/apikey)")

    st.divider()

    tool = st.selectbox(
        "ツールを選択",
        [
            "📝 ブログ記事作成",
            "📧 メール返信文生成",
            "📋 文章要約",
            "📱 SNS投稿文生成",
            "✅ 文章校正・改善",
            "💡 タイトル・見出し生成",
            "🎨 トーン変換",
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("使用モデル: gemini-2.0-flash")


# --- ヘルパー ---
def check_api():
    if not st.session_state.api_key:
        st.warning("サイドバーにGemini APIキーを入力してください。")
        return False
    return True


def stream_gemini(system_prompt: str, user_prompt: str):
    client = genai.Client(api_key=st.session_state.api_key)
    try:
        response = client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"\n\n**エラーが発生しました：** {e}\n\nAPIキーが正しいか確認してください。"


# --- ツール: ブログ記事作成 ---
def tool_blog():
    st.header("📝 ブログ記事作成")
    st.caption("テーマを入力するだけで、読まれるブログ記事を生成します")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        topic = st.text_input("テーマ・キーワード *", placeholder="例：在宅ワークの生産性を上げる方法")
        audience = st.text_input("対象読者", placeholder="例：副業を始めたい20〜30代の会社員")
        length = st.selectbox("文字数の目安", ["短め（500〜800文字）", "標準（1000〜1500文字）", "長め（2000〜3000文字）"])
        tone = st.selectbox("トーン", ["親しみやすい", "プロフェッショナル", "教育的・解説調"])
        notes = st.text_area("補足情報（任意）", placeholder="含めたいポイントやエピソードなど", height=100)
        generate = st.button("✨ 記事を生成", type="primary", use_container_width=True)

    with col2:
        st.subheader("生成結果")
        if generate:
            if not check_api():
                return
            if not topic:
                st.error("テーマ・キーワードを入力してください")
                return

            system = (
                "あなたはプロのブログライターです。SEOを意識しつつ、読者を引きつける魅力的なブログ記事を"
                "日本語で書きます。マークダウン形式（H2・H3見出し）で整理して出力してください。"
            )
            prompt = f"""以下の条件でブログ記事を書いてください。

テーマ：{topic}
対象読者：{audience or '一般的な読者'}
文字数目安：{length}
トーン：{tone}
補足情報：{notes or 'なし'}

構成：キャッチーなタイトル → リード文 → 本文（見出し複数） → まとめ"""

            st.write_stream(stream_gemini(system, prompt))


# --- ツール: メール返信文生成 ---
def tool_email():
    st.header("📧 メール返信文生成")
    st.caption("受信したメールに対する返信文を自動で作成します")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        received = st.text_area("受信メールの内容 *", placeholder="返信したいメールの内容を貼り付けてください", height=220)
        direction = st.text_input("返信の方向性", placeholder="例：承認する、丁重に断る、詳細を確認する")
        tone = st.selectbox("トーン", ["丁寧・フォーマル", "普通", "カジュアル"])
        sender = st.text_input("差出人名（任意）", placeholder="例：田中太郎")
        generate = st.button("✨ 返信文を生成", type="primary", use_container_width=True)

    with col2:
        st.subheader("生成結果")
        if generate:
            if not check_api():
                return
            if not received:
                st.error("受信メールの内容を入力してください")
                return

            system = "あなたはビジネスメールの専門家です。受信メールに対して、自然で適切な返信文を日本語で作成します。"
            prompt = f"""以下のメールへの返信文を作成してください。

【受信メール】
{received}

返信の方向性：{direction or '適切に対応する'}
トーン：{tone}
差出人名：{sender or '（省略）'}

件名と本文を含む完全な返信メールを作成してください。"""

            st.write_stream(stream_gemini(system, prompt))


# --- ツール: 文章要約 ---
def tool_summary():
    st.header("📋 文章要約")
    st.caption("長い文章を要点を押さえて簡潔にまとめます")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        text = st.text_area("要約したい文章 *", placeholder="要約したい文章を貼り付けてください", height=280)
        length = st.selectbox("要約の長さ", ["短め（3〜5行）", "標準（5〜10行）", "詳細（箇条書き付き）"])
        fmt = st.selectbox("出力形式", ["文章形式", "箇条書き", "両方（文章 + 要点）"])
        generate = st.button("✨ 要約する", type="primary", use_container_width=True)

    with col2:
        st.subheader("生成結果")
        if generate:
            if not check_api():
                return
            if not text:
                st.error("要約したい文章を入力してください")
                return

            system = "あなたは文章の要約専門家です。重要なポイントを逃さず、簡潔にまとめることが得意です。日本語で出力します。"
            prompt = f"""以下の文章を要約してください。

【文章】
{text}

要約の長さ：{length}
出力形式：{fmt}"""

            st.write_stream(stream_gemini(system, prompt))


# --- ツール: SNS投稿文生成 ---
def tool_sns():
    st.header("📱 SNS投稿文生成")
    st.caption("X・Instagram・Facebook・noteなど各SNS向けの投稿文を生成します")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        content = st.text_area("伝えたいこと *", placeholder="投稿で伝えたい内容や出来事を入力してください", height=130)
        platform = st.selectbox("プラットフォーム", ["X（Twitter）", "Instagram", "Facebook", "LINE オープンチャット", "note"])
        tone = st.selectbox("トーン", ["カジュアル・親しみやすい", "プロフェッショナル", "感情的・共感重視", "情報共有・教育的"])
        hashtags = st.text_input("希望するハッシュタグ（任意）", placeholder="例：在宅ワーク, 副業, フリーランス")
        generate = st.button("✨ 投稿文を生成", type="primary", use_container_width=True)

    with col2:
        st.subheader("生成結果")
        if generate:
            if not check_api():
                return
            if not content:
                st.error("伝えたいことを入力してください")
                return

            notes = {
                "X（Twitter）": "140文字以内を意識。長い場合はスレッド形式で分割してください。",
                "Instagram": "改行を多用してリーダビリティを高め、ハッシュタグは最後にまとめてください。",
                "Facebook": "少し長めで、親しみやすい文体で書いてください。",
                "LINE オープンチャット": "短く・読みやすく・親しみやすい口調で書いてください。",
                "note": "ブログ風の読みやすい文体で、見出しも使って整理してください。",
            }

            system = f"あなたはSNSマーケティングの専門家です。エンゲージメントが高い投稿文を日本語で作成します。{notes.get(platform, '')}"
            prompt = f"""以下の内容でSNS投稿文を作成してください。

プラットフォーム：{platform}
伝えたいこと：{content}
トーン：{tone}
ハッシュタグ希望：{hashtags or 'AIが適切に選定'}"""

            st.write_stream(stream_gemini(system, prompt))


# --- ツール: 文章校正・改善 ---
def tool_proofread():
    st.header("✅ 文章校正・改善")
    st.caption("誤字脱字のチェックと文章の読みやすさ・自然さを改善します")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        text = st.text_area("校正したい文章 *", placeholder="校正・改善したい文章を入力してください", height=280)
        focus = st.selectbox("改善の重点", [
            "総合（誤字・文法・読みやすさ）",
            "誤字脱字のみ",
            "読みやすさ・流れの改善",
            "フォーマル度を上げる",
            "簡潔にする（冗長な表現を削る）"
        ])
        generate = st.button("✨ 校正・改善する", type="primary", use_container_width=True)

    with col2:
        st.subheader("生成結果")
        if generate:
            if not check_api():
                return
            if not text:
                st.error("校正したい文章を入力してください")
                return

            system = "あなたはプロの校正者・編集者です。文章の誤りを正確に指摘し、より良い表現に改善します。日本語で出力します。"
            prompt = f"""以下の文章を校正・改善してください。

【文章】
{text}

改善の重点：{focus}

出力形式：
1. 改善後の文章（全文）
2. 主な修正・改善ポイント（箇条書き）"""

            st.write_stream(stream_gemini(system, prompt))


# --- ツール: タイトル・見出し生成 ---
def tool_title():
    st.header("💡 タイトル・見出し生成")
    st.caption("記事・ブログ・資料のタイトルや見出し案を複数提案します")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        content = st.text_area("記事・コンテンツの概要 *", placeholder="記事の内容や伝えたいことを入力してください", height=160)
        use_case = st.selectbox("用途", ["ブログ記事", "SNS投稿", "メール件名", "YouTube動画タイトル", "資料・レポート"])
        count = st.selectbox("提案数", ["5案", "10案", "15案"])
        generate = st.button("✨ タイトルを生成", type="primary", use_container_width=True)

    with col2:
        st.subheader("生成結果")
        if generate:
            if not check_api():
                return
            if not content:
                st.error("コンテンツの概要を入力してください")
                return

            system = "あなたはコピーライターです。クリックしたくなる、魅力的なタイトルを作るのが得意です。日本語で出力します。"
            prompt = f"""以下のコンテンツに合うタイトルを{count}提案してください。

【コンテンツの概要】
{content}

用途：{use_case}

各タイトルに、効果的な理由を一言コメントも添えてください。番号付きリストで出力してください。"""

            st.write_stream(stream_gemini(system, prompt))


# --- ツール: トーン変換 ---
def tool_tone():
    st.header("🎨 トーン変換")
    st.caption("文章のトーン・スタイルを変換します（フォーマル⇔カジュアルなど）")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        text = st.text_area("変換したい文章 *", placeholder="トーンを変換したい文章を入力してください", height=220)
        target_tone = st.selectbox("変換後のトーン", [
            "フォーマル・丁寧",
            "カジュアル・砕けた",
            "フレンドリー・親しみやすい",
            "説得力がある・力強い",
            "シンプル・わかりやすい",
            "ビジネスライク・簡潔",
        ])
        audience = st.text_input("対象（任意）", placeholder="例：上司、友人、お客様")
        generate = st.button("✨ トーンを変換", type="primary", use_container_width=True)

    with col2:
        st.subheader("生成結果")
        if generate:
            if not check_api():
                return
            if not text:
                st.error("変換したい文章を入力してください")
                return

            system = "あなたは文章のトーン・スタイル変換の専門家です。内容を変えずに、指定されたトーンに変換します。日本語で出力します。"
            prompt = f"""以下の文章のトーンを変換してください。

【元の文章】
{text}

変換後のトーン：{target_tone}
対象読者・相手：{audience or '指定なし'}

変換後の文章のみを出力してください。"""

            st.write_stream(stream_gemini(system, prompt))


# --- ルーティング ---
tool_map = {
    "📝 ブログ記事作成": tool_blog,
    "📧 メール返信文生成": tool_email,
    "📋 文章要約": tool_summary,
    "📱 SNS投稿文生成": tool_sns,
    "✅ 文章校正・改善": tool_proofread,
    "💡 タイトル・見出し生成": tool_title,
    "🎨 トーン変換": tool_tone,
}

tool_map[tool]()
