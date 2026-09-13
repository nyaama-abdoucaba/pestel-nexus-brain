from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

from postgres import UiPostgresError

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from views import infrastructure, linkedin_posts, linkedin_targets


st.set_page_config(
    page_title="Nexus UI",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="expanded",
)


VIEWS = {
    "Cibles LinkedIn": linkedin_targets.render,
    "Posts LinkedIn": linkedin_posts.render,
    "Infrastructure": infrastructure.render,
}


def main() -> None:
    st.sidebar.title("Nexus UI")

    display_labels = {
        "Cibles LinkedIn": "Cibles LinkedIn",
        "Posts LinkedIn": "Posts LinkedIn",
        "Infrastructure": "Infrastructure",
    }

    view_keys = list(VIEWS.keys())
    selected_view = st.sidebar.radio(
        "Vue",
        options=view_keys,
        format_func=lambda k: display_labels.get(k, k),
    )

    try:
        VIEWS[selected_view]()
    except UiPostgresError as exc:
        st.error(str(exc))


if __name__ == "__main__":
    main()
