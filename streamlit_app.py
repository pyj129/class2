import math
from fractions import Fraction

import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="삼각함수 그래프 변환 시뮬레이터", layout="wide")

DEFAULTS = {
    "a": 1,
    "b": 1,
    "m": 0.0,
    "n": 0.0,
}

SPECIAL_M_OPTIONS = [
    (-math.pi, r"$-\pi$"),
    (-math.pi / 2, r"$-\frac{\pi}{2}$"),
    (-math.pi / 3, r"$-\frac{\pi}{3}$"),
    (-math.pi / 4, r"$-\frac{\pi}{4}$"),
    (-math.pi / 6, r"$-\frac{\pi}{6}$"),
    (0.0, r"$0$"),
    (math.pi / 6, r"$\frac{\pi}{6}$"),
    (math.pi / 4, r"$\frac{\pi}{4}$"),
    (math.pi / 3, r"$\frac{\pi}{3}$"),
    (math.pi / 2, r"$\frac{\pi}{2}$"),
    (math.pi, r"$\pi$"),
]
SPECIAL_M_LABELS = {value: label for value, label in SPECIAL_M_OPTIONS}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def format_coefficient(value: float) -> str:
    if abs(value - round(value)) < 1e-8:
        return str(int(round(value)))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def format_radian(value: float) -> str:
    if abs(value) < 1e-8:
        return "0"
    units = int(round(value / (math.pi / 12)))
    frac = Fraction(abs(units), 12)
    numerator = frac.numerator
    denominator = frac.denominator
    sign = "-" if units < 0 else ""
    if numerator == denominator:
        return f"{sign}\\pi"
    if numerator == 0:
        return "0"
    if denominator == 1:
        return f"{sign}{numerator}\\pi"
    return f"{sign}\\frac{{{numerator}\\pi}}{{{denominator}}}"


def format_m_text(value: float) -> str:
    return SPECIAL_M_LABELS.get(value, format_radian(value))


def build_function_formula(function_type: str, a: float, b: float, m: float, n: float) -> str:
    a_str = format_coefficient(a)
    b_str = format_coefficient(b)
    if abs(m) < 1e-8:
        inner = f"x"
    elif m > 0:
        inner = f"x - {format_radian(m)}"
    else:
        inner = f"x + {format_radian(abs(m))}"
    n_part = f" + {format_coefficient(n)}" if n >= 0 else f" - {format_coefficient(abs(n))}"
    return f"y = {a_str}\\{function_type}({b_str}({inner})){n_part}"


def build_period_text(b: float) -> tuple[str, str]:
    if b == 0:
        return "\\infty", "\\infty"
    abs_b = abs(b)
    
    if abs(b - round(b)) < 1e-8:  # 정수
        b_int = abs(int(round(b)))
        if b_int == 1:
            fraction = "2\\pi"
        else:
            fraction = f"\\frac{{2\\pi}}{{{b_int}}}"
    else:  # 실수
        b_coeff = format_coefficient(abs_b)
        if b_coeff == "1":
            fraction = "2\\pi"
        else:
            fraction = f"\\frac{{2\\pi}}{{{b_coeff}}}"
    
    decimal = format_coefficient(2 * math.pi / abs_b)
    return fraction, decimal


def build_plot(function_type: str, a: float, b: float, m: float, n: float) -> go.Figure:
    x = np.linspace(-2 * np.pi, 2 * np.pi, 800)
    if function_type == "sin":
        base_y = np.sin(x)
        transformed_y = a * np.sin(b * (x - m)) + n
    else:
        base_y = np.cos(x)
        transformed_y = a * np.cos(b * (x - m)) + n

    max_value = abs(a) + n
    min_value = -abs(a) + n

    y_tick_values = list(range(-5, 6))
    for value in (max_value, min_value):
        if -5 <= value <= 5 and all(abs(value - v) > 1e-8 for v in y_tick_values):
            y_tick_values.append(value)
    y_tick_values = sorted(y_tick_values)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=base_y,
            mode="lines",
            name=f"Base: {function_type}(x)",
            line=dict(color="rgba(0, 0, 0, 0.22)", dash="dash", width=3),
            hovertemplate="x: %{x:.2f}<br>y: %{y:.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=transformed_y,
            mode="lines",
            name="Transformed",
            line=dict(color="#1f77b4", width=4),
            hovertemplate="x: %{x:.2f}<br>y: %{y:.2f}<extra></extra>",
        )
    )

    fig.add_hline(y=1, line=dict(color="gray", dash="dot"), opacity=0.6)
    fig.add_hline(y=-1, line=dict(color="gray", dash="dot"), opacity=0.6)
    fig.add_hline(y=max_value, line=dict(color="green", dash="dash"), opacity=0.7)
    fig.add_hline(y=min_value, line=dict(color="red", dash="dash"), opacity=0.7)

    tick_values = [-2 * np.pi, -np.pi, -np.pi / 2, 0, np.pi / 2, np.pi, 2 * np.pi]
    tick_text = [r"$-2\pi$", r"$-\pi$", r"$-\frac{\pi}{2}$", r"$0$", r"$\frac{\pi}{2}$", r"$\pi$", r"$2\pi$"]

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=tick_values,
            ticktext=tick_text,
            gridcolor="#e6e6e6",
            zeroline=True,
            zerolinecolor="#888",
            tickfont=dict(size=16),
            title_text="x (rad)",
            title_font=dict(size=18),
        ),
        yaxis=dict(
            range=[-5, 5],
            tickmode="array",
            tickvals=y_tick_values,
            tickfont=dict(size=16),
            title_text="y",
            title_font=dict(size=18),
            gridcolor="#e6e6e6",
            zeroline=True,
            zerolinecolor="#888",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=30, b=40, l=40, r=40),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=16),
        hovermode="x unified",
    )
    return fig


def main() -> None:
    st.title("삼각함수 그래프 변환 시뮬레이터")
    st.markdown(
        "이 수업용 앱은 `y = a \\sin(b(x - m)) + n` 및 `y = a \\cos(b(x - m)) + n`의 변화를 직관적으로 탐구하도록 제작되었습니다."
    )

    with st.sidebar:
        st.header("매개변수 제어")
        function_type = st.radio(
            "기본 함수 선택",
            ("sin", "cos"),
            index=0,
            format_func=lambda f: f"{f}(x)",
        )

        a = st.slider("a (진폭)", -3, 3, st.session_state.a, step=1, key="a")
        b = st.slider("b (계수)", -5, 5, st.session_state.b, step=1, key="b")
        m = st.select_slider(
            "m (평행이동: 특수각 모드)",
            options=[value for value, _ in SPECIAL_M_OPTIONS],
            value=st.session_state.m,
            format_func=format_m_text,
            key="m",
        )
        n = st.slider("n (y축 이동)", -5.0, 5.0, st.session_state.n, step=0.1, key="n")

        if st.button("초기화"):
            st.session_state.clear()
            st.rerun()

        st.markdown(f"**현재 m 값:** $m = {format_m_text(m)}$")
        if b == 0:
            st.warning("b=0일 때 주기는 무한대가 되어 그래프가 상수 함수가 됩니다.")

    period_fraction, period_decimal = build_period_text(b)
    max_value = abs(a) + n
    min_value = -abs(a) + n

    fig = build_plot(function_type, a, b, m, n)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 실시간 함수식")
    st.latex(build_function_formula(function_type, a, b, m, n))

    st.markdown("### 현재 상태 정보")
    st.write(f"- 최대값: $|a| + n = {format_coefficient(abs(a))} + {format_coefficient(n)} = {format_coefficient(max_value)}$")
    st.write(f"- 최소값: $-|a| + n = -{format_coefficient(abs(a))} + {format_coefficient(n)} = {format_coefficient(min_value)}$")
    if b == 0:
        st.write("- 주기: ∞ (b=0일 때 주기가 무한대입니다)")
    else:
        st.write(f"- 주기: ${period_fraction}$ ≈ {period_decimal}")

    if a < 0:
        st.info("a가 음수이면 그래프가 x축에 대하여 대칭 이동된 형태입니다.")
    if b < 0:
        st.info("b가 음수이면 그래프가 y축 대칭 변환 형태입니다.")
    if b == 0:
        st.info("b=0이면 함수는 상수 함수가 됩니다. 이 경우 주기가 정의되지 않습니다.")

    st.markdown("---")
    st.markdown("#### 교사용 팁")
    st.write(
        "- x축 눈금은 라디안 기호로 표시됩니다. 수업 중에 π 단위를 바로 확인할 수 있습니다."
    )
    st.write(
        "- a와 b는 정수 단위로 설정되어 있어 슬라이더 조절이 딱딱 끊겨서 변화를 설명하기 쉽습니다."
    )
    st.write(
        "- m은 특수각 모드로 구성되어 있어 평행이동을 직관적으로 보여줍니다."
    )


if __name__ == "__main__":
    main()
