from __future__ import annotations

import streamlit as st

from postgres import (
    UiPostgresError,
    count_linkedin_posts,
    fetchall,
    get_linkedin_post,
    list_linkedin_posts,
    list_post_statuses,
    list_target_categories,
)


def _load_authors() -> list[dict]:
    try:
        return fetchall(
            "SELECT id, name FROM linkedin_targets ORDER BY name"
        )
    except UiPostgresError:
        return []


def render() -> None:
    st.title("Posts LinkedIn")

    try:
        statuses = list_post_statuses()
        categories = list_target_categories()
        authors = _load_authors()
    except UiPostgresError as exc:
        st.error(str(exc))
        return

    cat_options = {c["slug"]: c.get("label") or c["slug"] for c in categories}
    author_options = {str(a["id"]): a["name"] for a in authors}

    # ── Filtres ───────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    search = col1.text_input("Rechercher", key="post_search", placeholder="Texte ou auteur")
    author_filter = col2.selectbox(
        "Auteur",
        ["Tous", *author_options.keys()],
        format_func=lambda k: "Tous" if k == "Tous" else author_options.get(k, k),
        key="post_author",
    )
    cat_filter = col3.selectbox(
        "Catégorie",
        ["Toutes", *cat_options.keys()],
        format_func=lambda k: "Toutes" if k == "Toutes" else cat_options.get(k, k),
        key="post_cat",
    )
    status_filter = col4.selectbox("Statut", ["Tous", *statuses], key="post_status")

    col5, col6, col7 = st.columns([1, 1, 1])
    date_from = col5.date_input("Publié depuis", value=None, key="post_date_from")
    date_to = col6.date_input("Jusqu'au", value=None, key="post_date_to")
    page_size = col7.selectbox("Par page", [10, 25, 50], index=0, key="post_page_size")

    if col1.button("Rafraîchir", key="post_refresh"):
        st.session_state.pop("post_page", None)
        st.rerun()

    # ── Filtres → dict ────────────────────────────────────────────────────────
    filters: dict = {}
    if search:
        filters["search"] = search
    if author_filter != "Tous":
        filters["author_id"] = author_filter
    if cat_filter != "Toutes":
        filters["category"] = cat_filter
    if status_filter != "Tous":
        filters["status"] = status_filter
    if date_from:
        filters["date_from"] = date_from
    if date_to:
        filters["date_to"] = date_to

    filter_sig = (search, author_filter, cat_filter, status_filter, date_from, date_to, page_size)
    if st.session_state.get("post_filter_sig") != filter_sig:
        st.session_state["post_filter_sig"] = filter_sig
        st.session_state["post_page"] = 0

    page = st.session_state.setdefault("post_page", 0)
    offset = page * page_size

    # ── Données ───────────────────────────────────────────────────────────────
    try:
        total = count_linkedin_posts(filters)
        rows = list_linkedin_posts(filters, limit=page_size, offset=offset)
    except UiPostgresError as exc:
        st.error(str(exc))
        return

    total_pages = max(1, (total + page_size - 1) // page_size)

    # ── Navigation pages ──────────────────────────────────────────────────────
    nav1, nav2, nav3 = st.columns([1, 1, 8])
    if nav1.button("Précédent", disabled=(page == 0), key="post_prev"):
        st.session_state["post_page"] = max(0, page - 1)
        st.rerun()
    if nav2.button("Suivant", disabled=(page >= total_pages - 1), key="post_next"):
        st.session_state["post_page"] = page + 1
        st.rerun()
    nav3.caption(f"Page {page + 1} / {total_pages} — {total} post(s)")

    # ── Tableau ───────────────────────────────────────────────────────────────
    if not rows:
        st.info("Aucun post pour ces filtres.")
        return

    display = [
        {
            "Auteur": r["author_name"],
            "Extrait": (r["text"] or "")[:120],
            "Publié le": str(r["posted_at"] or "–"),
            "Observé le": str(r["observed_at"] or "–"),
            "Statut": r["status"] or "–",
            "Lien": r["url"] or "",
            "_id": str(r["id"]),
        }
        for r in rows
    ]

    import pandas as pd

    frame = pd.DataFrame(display)
    visible = frame.drop(columns=["_id"])

    try:
        event = st.dataframe(
            visible,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config={
                "Lien": st.column_config.LinkColumn(display_text="post"),
            },
        )
        sel = event.selection.get("rows", []) if event else []
        selected_idx = sel[0] if sel else None
    except TypeError:
        st.dataframe(visible, use_container_width=True, hide_index=True)
        selected_idx = None

    # ── Détail ────────────────────────────────────────────────────────────────
    if selected_idx is not None and 0 <= selected_idx < len(display):
        post_id = display[selected_idx]["_id"]
        try:
            post = get_linkedin_post(post_id)
        except UiPostgresError as exc:
            st.error(str(exc))
            return
        if post:
            _render_detail(post)


def _render_detail(post: dict) -> None:
    st.divider()
    c1, c2 = st.columns(2)
    author_url = post.get("author_linkedin_url") or ""
    c1.markdown(
        f"**Auteur** : [{post['author_name']}]({author_url})" if author_url
        else f"**Auteur** : {post['author_name']}"
    )
    post_url = post.get("url") or ""
    if post_url:
        c1.markdown(f"**Post** : [Ouvrir]({post_url})")
    c2.markdown(f"**Statut** : {post.get('status') or '–'}")
    c2.markdown(f"**Publié le** : {post.get('posted_at') or '–'}")
    c2.markdown(f"**Observé le** : {post.get('observed_at') or '–'}")
    st.markdown("---")
    st.text(post.get("text") or "")
    st.caption(
        f"Créé le {post['created_at']} — Modifié le {post['updated_at']}"
    )
    with st.expander("Payload brut", expanded=False):
        st.json(post.get("raw_payload") or {})
