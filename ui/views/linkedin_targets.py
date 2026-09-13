from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse

import streamlit as st

from postgres import (
    UiPostgresError,
    count_linkedin_targets,
    create_linkedin_target,
    get_linkedin_target,
    list_linkedin_targets,
    list_target_categories,
)

STATUSES = ["candidate", "active", "paused", "rejected"]
_LINKEDIN_PROFILE_RE = re.compile(
    r"^https?://(www\.)?linkedin\.com/in/[^/?#]+/?$", re.IGNORECASE
)


def normalize_linkedin_url(raw: str) -> str:
    raw = raw.strip()
    parsed = urlparse(raw)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("URL invalide : doit commencer par https://")
    host = parsed.netloc.lower()
    if host != "linkedin.com" and not host.endswith(".linkedin.com"):
        raise ValueError("L'URL doit appartenir à linkedin.com")
    path = parsed.path.rstrip("/")
    if not path.startswith("/in/") or len(path) <= len("/in/"):
        raise ValueError("L'URL doit être un profil LinkedIn (linkedin.com/in/...)")
    return urlunparse(("https", "www.linkedin.com", path, "", "", ""))


def _load_categories() -> list[dict]:
    try:
        return list_target_categories()
    except UiPostgresError:
        return []


def render() -> None:
    st.title("Cibles LinkedIn")

    categories = _load_categories()
    cat_options = {c["slug"]: c.get("label") or c["slug"] for c in categories}

    # ── Filtres ──────────────────────────────────────────────────────────────
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    search = col1.text_input("Rechercher", key="tgt_search", placeholder="Nom ou URL")
    status_filter = col2.selectbox("Statut", ["Tous", *STATUSES], key="tgt_status")
    cat_filter = col3.selectbox(
        "Catégorie",
        ["Toutes", *cat_options.keys()],
        format_func=lambda k: "Toutes" if k == "Toutes" else cat_options.get(k, k),
        key="tgt_cat",
    )
    scrape_filter = col4.selectbox(
        "Scraping", ["Tous", "Activé", "Désactivé"], key="tgt_scrape"
    )
    page_size = col5.selectbox("Par page", [10, 25, 50], index=0, key="tgt_page_size")

    if col1.button("Rafraîchir", key="tgt_refresh"):
        st.session_state.pop("tgt_page", None)
        st.rerun()

    # ── Bouton Ajouter ───────────────────────────────────────────────────────
    with st.expander("Ajouter une cible", expanded=False):
        _render_add_form(cat_options)

    # ── Filtres → dict ────────────────────────────────────────────────────────
    filters: dict = {}
    if search:
        filters["search"] = search
    if status_filter != "Tous":
        filters["status"] = status_filter
    if cat_filter != "Toutes":
        filters["category"] = cat_filter
    if scrape_filter == "Activé":
        filters["scrape_enabled"] = True
    elif scrape_filter == "Désactivé":
        filters["scrape_enabled"] = False

    # Réinitialise la page si les filtres changent
    filter_sig = (search, status_filter, cat_filter, scrape_filter, page_size)
    if st.session_state.get("tgt_filter_sig") != filter_sig:
        st.session_state["tgt_filter_sig"] = filter_sig
        st.session_state["tgt_page"] = 0

    page = st.session_state.setdefault("tgt_page", 0)
    offset = page * page_size

    # ── Données ───────────────────────────────────────────────────────────────
    try:
        total = count_linkedin_targets(filters)
        rows = list_linkedin_targets(filters, limit=page_size, offset=offset)
    except UiPostgresError as exc:
        st.error(str(exc))
        return

    total_pages = max(1, (total + page_size - 1) // page_size)

    # ── Navigation pages ──────────────────────────────────────────────────────
    nav1, nav2, nav3 = st.columns([1, 1, 8])
    if nav1.button("Précédent", disabled=(page == 0), key="tgt_prev"):
        st.session_state["tgt_page"] = max(0, page - 1)
        st.rerun()
    if nav2.button("Suivant", disabled=(page >= total_pages - 1), key="tgt_next"):
        st.session_state["tgt_page"] = page + 1
        st.rerun()
    nav3.caption(f"Page {page + 1} / {total_pages} — {total} cible(s)")

    # ── Tableau ───────────────────────────────────────────────────────────────
    if not rows:
        st.info("Aucune cible pour ces filtres.")
        return

    display = [
        {
            "Nom": r["name"],
            "Catégories": r["categories"],
            "Statut": r["status"],
            "Scraping": "✓" if r["scrape_enabled"] else "–",
            "Dernier scraping": str(r["last_scraped_at"] or "–"),
            "LinkedIn": r["linkedin_url"],
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
                "LinkedIn": st.column_config.LinkColumn(display_text="profil"),
            },
        )
        sel = event.selection.get("rows", []) if event else []
        selected_idx = sel[0] if sel else None
    except TypeError:
        st.dataframe(visible, use_container_width=True, hide_index=True)
        selected_idx = None

    # ── Détail ────────────────────────────────────────────────────────────────
    if selected_idx is not None and 0 <= selected_idx < len(display):
        target_id = display[selected_idx]["_id"]
        try:
            target = get_linkedin_target(target_id)
        except UiPostgresError as exc:
            st.error(str(exc))
            return
        if target:
            _render_detail(target)


def _render_detail(target: dict) -> None:
    st.divider()
    st.subheader(target["name"])
    c1, c2 = st.columns(2)
    c1.markdown(f"**LinkedIn** : [{target['linkedin_url']}]({target['linkedin_url']})")
    c1.markdown(f"**Statut** : {target['status']}")
    c1.markdown(f"**Scraping** : {'Activé' if target['scrape_enabled'] else 'Désactivé'}")
    c2.markdown(f"**Catégories** : {target['categories'] or '–'}")
    c2.markdown(f"**Dernier scraping** : {target['last_scraped_at'] or '–'}")
    if target.get("why_follow"):
        st.markdown(f"**Pourquoi la suivre** : {target['why_follow']}")
    st.caption(
        f"Créée le {target['created_at']} — Modifiée le {target['updated_at']}"
    )
    with st.expander("Métadonnées", expanded=False):
        st.json(target.get("metadata") or {})


def _render_add_form(cat_options: dict[str, str]) -> None:
    with st.form("add_target_form", clear_on_submit=True):
        name = st.text_input("Nom *")
        url_raw = st.text_input("URL LinkedIn *", placeholder="https://www.linkedin.com/in/...")
        why_follow = st.text_area("Pourquoi la suivre", height=80)
        selected_cats = st.multiselect(
            "Catégories *",
            options=list(cat_options.keys()),
            default=["ai_practitioner"] if "ai_practitioner" in cat_options else [],
            format_func=lambda k: cat_options.get(k, k),
        )
        status = st.selectbox("Statut *", STATUSES, index=0)
        scrape_enabled = st.checkbox("Scraping activé", value=False)

        submitted = st.form_submit_button("Ajouter")

    if not submitted:
        return

    # Validation
    errors: list[str] = []
    if not name.strip():
        errors.append("Le nom est obligatoire.")
    if not selected_cats:
        errors.append("Au moins une catégorie est requise.")
    try:
        linkedin_url = normalize_linkedin_url(url_raw)
    except ValueError as exc:
        errors.append(str(exc))
        linkedin_url = ""

    if errors:
        for e in errors:
            st.error(e)
        return

    try:
        create_linkedin_target(
            {
                "name": name.strip(),
                "linkedin_url": linkedin_url,
                "why_follow": why_follow.strip() or None,
                "status": status,
                "scrape_enabled": scrape_enabled,
            },
            category_slugs=selected_cats,
        )
        st.success(f"Cible « {name.strip()} » ajoutée.")
        st.session_state["tgt_page"] = 0
        st.rerun()
    except UiPostgresError as exc:
        if "unique_violation" in str(exc):
            st.error("Cette cible LinkedIn existe déjà.")
        else:
            st.error(str(exc))
