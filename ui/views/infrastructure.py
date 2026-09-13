from __future__ import annotations

import streamlit as st

from infra import check_service, docker_logs, load_services

_STATUS_ICON = {"up": "🟢", "down": "🔴", "unknown": "⚪"}


def render() -> None:
    st.title("Infrastructure")

    services = load_services()

    if st.button("Rafraîchir", key="infra_refresh"):
        st.session_state.pop("infra_results", None)
        st.rerun()

    if "infra_results" not in st.session_state:
        with st.spinner("Sondage en cours…"):
            st.session_state["infra_results"] = [
                {"svc": svc, "result": check_service(svc)} for svc in services
            ]

    entries = st.session_state["infra_results"]

    for entry in entries:
        svc = entry["svc"]
        res = entry["result"]

        icon = _STATUS_ICON.get(res["status"], "⚪")
        latency = f"{res['latency_ms']} ms" if res["latency_ms"] is not None else "–"
        runtime_badge = f"`{svc['runtime']}`"
        port_info = (
            f":{svc['port_host']}" if svc.get("port_host") else ""
        )

        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        col1.markdown(f"{icon} **{svc['name']}** {runtime_badge}  \n{svc['role']}")
        col2.markdown(f"**Latence**  \n{latency}")
        col3.markdown(f"**Port hôte**  \n{port_info or '–'}")

        url_browser = svc.get("url_browser")
        if url_browser:
            col4.link_button("Ouvrir", url_browser, use_container_width=True)
        else:
            col4.markdown("&nbsp;")

        with st.expander(f"Détail — {svc['name']}", expanded=False):
            st.markdown(f"**Healthcheck** : `{res['detail']}`")
            st.markdown(f"**Réseau** : `{svc.get('network') or '–'}`")

            native_url = svc.get("url_from_native")
            container_url = svc.get("url_from_container")
            n8n_url = svc.get("url_from_n8n")
            if native_url:
                st.markdown(f"**Natif** : `{native_url}`")
            if container_url:
                st.markdown(f"**Conteneur** : `{container_url}`")
            if n8n_url:
                st.markdown(f"**n8n** : `{n8n_url}`")

            compose_file = svc.get("compose")
            if compose_file:
                st.markdown(f"**Compose** : `{compose_file}`")
            start_cmd = svc.get("start")
            if start_cmd:
                st.code(start_cmd, language="bash")

            container = svc.get("container")
            if container:
                if st.button(f"Voir logs — {container}", key=f"logs_{svc['name']}"):
                    logs = docker_logs(container)
                    st.code(logs or "(aucun log)")

        st.divider()
