"""Interface web simples para apresentar o Telos."""

from __future__ import annotations

import json
import os
import re
import tempfile
import threading
import time
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, jsonify, render_template, request

import telos


telos.load_env_file()
ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("TELOS_DATA_DIR", ROOT / ".telos_web_data"))
LATEST_FILE = DATA_DIR / "ultima_rodada.json"
EMAIL_RATE_FILE = DATA_DIR / "limite_envios_email.json"
DEMO_ROUND_FILE = ROOT / "demo_round.json"
TELOS_HOSPEDADO = os.environ.get("TELOS_HOSPEDADO", "false").strip().lower() in {"1", "true", "yes", "on"}
DEMO_MODE = TELOS_HOSPEDADO or os.environ.get("TELOS_DEMO_MODE", "true").strip().lower() in {"1", "true", "yes", "on"}
CLIENT_MAP_FILE = Path(os.environ.get("TELOS_CLIENT_MAP_FILE", ROOT / ".telos_clientes.json"))
CASE_AREAS = {
    "imobiliario": range(1, 8),
    "empresarial": range(8, 13),
    "bancario": range(14, 17),
    "todas": (*range(1, 13), *range(14, 17)),
}
AREA_TERM_ENV = {
    "imobiliario": "TJSP_SEARCH_TERMS_IMOBILIARIO",
    "empresarial": "TJSP_SEARCH_TERMS_EMPRESARIAL",
    "bancario": "TJSP_SEARCH_TERMS_BANCARIO",
}
app = Flask(
    __name__,
    template_folder=str(ROOT / "templates"),
    static_folder=str(ROOT / "static"),
    static_url_path="/static",
)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
RUN_LOCK = threading.Lock()
STATE_LOCK = threading.Lock()
EMAIL_RATE_LOCK = threading.Lock()
PENDING_EMAIL: dict | None = None


@app.context_processor
def static_asset_version() -> dict[str, str]:
    """Version local CSS URLs so a browser cannot keep an obsolete stylesheet."""
    stylesheet = ROOT / "static" / "style.css"
    try:
        version = str(stylesheet.stat().st_mtime_ns)
    except OSError:
        version = "1"
    return {"static_version": version}


def load_latest_round() -> dict | None:
    try:
        data = json.loads(LATEST_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


LATEST_ROUND = load_latest_round()
RUN_STATE = {
    "running": False,
    "phase": "idle",
    "message": "Pronto para vigiar o TJSP.",
    "progress_current": 0,
    "progress_total": 0,
    "last_round": LATEST_ROUND,
    "email_status": "none",
    "email_available": False,
}


def write_latest_round(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=DATA_DIR, delete=False
        ) as temporary:
            json.dump(data, temporary, ensure_ascii=False, indent=2, default=str)
            temporary.write("\n")
            temporary_name = temporary.name
        os.replace(temporary_name, LATEST_FILE)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)


def update_run(**changes) -> None:
    with STATE_LOCK:
        RUN_STATE.update(changes)


def reserve_hosted_email_slot() -> str | None:
    """Reserve one hosted email attempt, enforcing per-minute and daily limits."""
    if not TELOS_HOSPEDADO:
        return None
    now = time.time()
    today = datetime.now().astimezone().date()
    with EMAIL_RATE_LOCK:
        try:
            previous = json.loads(EMAIL_RATE_FILE.read_text(encoding="utf-8"))
            timestamps = [float(value) for value in previous if isinstance(value, (int, float))]
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            timestamps = []
        recent = [value for value in timestamps if 0 <= now - value < 60]
        today_values = [value for value in timestamps
                        if datetime.fromtimestamp(value).astimezone().date() == today]
        if recent:
            return "Limite de envio: aguarde um minuto antes de enviar outro e-mail."
        if len(today_values) >= 20:
            return "Limite diário de 20 envios atingido. Tente novamente amanhã."
        timestamps = today_values + [now]
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        temporary_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=DATA_DIR, delete=False
            ) as temporary:
                json.dump(timestamps, temporary)
                temporary.write("\n")
                temporary_name = temporary.name
            os.replace(temporary_name, EMAIL_RATE_FILE)
        finally:
            if temporary_name and os.path.exists(temporary_name):
                os.unlink(temporary_name)
    return None


def current_provider_settings() -> tuple[str, str, str]:
    provider = os.environ.get("AI_PROVIDER", "openai").strip().lower() or "openai"
    if provider == "openai":
        return provider, os.environ.get("OPENAI_API_KEY", "").strip(), (
            os.environ.get("OPENAI_MODEL", telos.DEFAULT_OPENAI_MODEL).strip()
            or telos.DEFAULT_OPENAI_MODEL
        )
    if provider == "groq":
        return provider, os.environ.get("GROQ_API_KEY", "").strip(), (
            os.environ.get("GROQ_MODEL", telos.DEFAULT_GROQ_MODEL).strip()
            or telos.DEFAULT_GROQ_MODEL
        )
    return provider, os.environ.get("GEMINI_API_KEY", "").strip(), (
        os.environ.get("GEMINI_MODEL", telos.DEFAULT_GEMINI_MODEL).strip()
        or telos.DEFAULT_GEMINI_MODEL
    )


def configured_terms(area: str) -> list[str]:
    if area == "todas":
        groups = [
            os.environ.get(AREA_TERM_ENV["bancario"], ""),
            os.environ.get(AREA_TERM_ENV["imobiliario"], ""),
            os.environ.get(AREA_TERM_ENV["empresarial"], ""),
        ]
        joined = ";".join(value for value in groups if value.strip())
        raw = joined or os.environ.get("TJSP_SEARCH_TERMS", "")
    else:
        raw = os.environ.get(AREA_TERM_ENV[area], "").strip()
        if not raw:
            all_terms = [
                term.strip()
                for term in os.environ.get("TJSP_SEARCH_TERMS", "").split(";")
                if term.strip()
            ]
            raw = ";".join(all_terms[:7] if area == "imobiliario" else all_terms[7:12])
    return [term.strip() for term in raw.split(";") if term.strip() and len(term.strip()) <= 120]


def case_number(path: Path) -> int | None:
    match = re.search(r"\d+", path.stem)
    return int(match.group()) if match else None


def cases_for_area(area: str) -> list[Path]:
    allowed = set(CASE_AREAS[area])
    result = []
    for path in sorted(telos.CASES_DIR.rglob("*.txt")):
        if not path.is_file():
            continue
        number = case_number(path)
        if number in allowed:
            result.append(path)
        else:
            try:
                text = telos.read_document(path)
            except Exception:
                continue
            match = re.search(r"(?m)^Área:\s*(imobiliario|empresarial|bancario)\s*$", text, re.I)
            if area == "todas" or (match and match.group(1).lower() == area):
                result.append(path)
    return result


def case_list() -> list[dict]:
    items = []
    client_map = load_client_map()
    for path in sorted(telos.CASES_DIR.rglob("*.txt")):
        try:
            content = telos.read_document(path)
        except (OSError, RuntimeError):
            continue
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        number = case_number(path)
        if number in CASE_AREAS["imobiliario"]:
            area = "Imobiliário"
        elif number in CASE_AREAS["empresarial"]:
            area = "Empresarial"
        elif number in CASE_AREAS["bancario"]:
            area = "Bancário"
        elif number == 13:
            area = "Caso de controle"
        else:
            area = "Caso de demonstração"
        record = client_map.get(path.stem, {})
        lines = [line for line in lines if not line.startswith(("Área:", "Tipo:", "Código:"))]
        title = telos.email_case_title(path.name)
        if record:
            title = f"{record.get('tipo', 'Caso')} — {record.get('nome_cliente', 'Cliente')}"
        if number not in (
            set(CASE_AREAS["imobiliario"])
            | set(CASE_AREAS["empresarial"])
            | set(CASE_AREAS["bancario"])
            | {13}
        ):
            area_match = re.search(r"(?m)^Área:\s*(imobiliario|empresarial|bancario)\s*$", content, re.I)
            area = "Imobiliário" if area_match and area_match.group(1).lower() == "imobiliario" else (
                "Empresarial" if area_match and area_match.group(1).lower() == "empresarial" else (
                    "Bancário" if area_match and area_match.group(1).lower() == "bancario" else "Caso de demonstração"
                )
            )
        items.append({
            "titulo": title,
            "descricao": " ".join(lines[1:]) if len(lines) > 1 else "Descrição não informada.",
            "area": area,
        })
    return items


CASE_MATCH_STOPWORDS = {
    "a", "à", "ao", "aos", "as", "com", "da", "das", "de", "do", "dos",
    "e", "em", "entre", "na", "nas", "no", "nos", "o", "os", "ou", "para",
    "pela", "pelas", "pelo", "pelos", "por", "que", "se", "sem", "um", "uma",
    "cliente", "caso", "quer", "empresa", "parte", "direito", "acao", "pedido",
}


def case_match_tokens(text: str) -> set[str]:
    folded = unicodedata.normalize("NFKD", text.casefold())
    plain = "".join(char for char in folded if not unicodedata.combining(char))
    return {word for word in re.findall(r"[a-z0-9]{3,}", plain) if word not in CASE_MATCH_STOPWORDS}


def demo_case_example(description: str, client_name: str, area: str) -> tuple[dict, dict] | None:
    """Choose an existing demo notice by transparent local word similarity."""
    try:
        fixture = json.loads(DEMO_ROUND_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    area_labels = {"imobiliario": "imobiliário", "empresarial": "empresarial", "bancario": "bancário"}
    candidates = []
    for decision in fixture.get("decisions", []):
        if decision.get("area", "").casefold() != area_labels.get(area):
            continue
        filename = decision.get("file", "")
        linked_alerts = [item for item in fixture.get("alerts", []) if item.get("decisao") == filename]
        chosen = next((item for item in linked_alerts
                       if telos.direct_alert_is_readable(item)
                       and telos.is_official_tjsp_link(item.get("link_oficial", ""))), None)
        if chosen is None:
            continue
        try:
            decision_text = telos.read_document(telos.DECISIONS_DIR / filename)
        except (OSError, RuntimeError):
            decision_text = ""
        evidence = " ".join(str(value) for value in chosen.get("trechos_relacao", []))
        comparison_text = " ".join([
            str(chosen.get("resumo", "")), str(chosen.get("motivo_relacao", "")),
            str(chosen.get("resultado", "")), evidence, decision_text[:30000],
        ])
        candidates.append((decision, chosen, comparison_text))
    if not candidates:
        return None

    query_tokens = case_match_tokens(description)
    candidate_tokens = [case_match_tokens(text) for _, _, text in candidates]
    document_frequency = {
        token: sum(token in terms for terms in candidate_tokens)
        for token in query_tokens
    }
    query_bigrams = set(zip(case_match_tokens_ordered(description), case_match_tokens_ordered(description)[1:]))
    ranked = []
    for index, (decision, chosen, _) in enumerate(candidates):
        overlap = sum(1.0 + (len(candidates) / (1 + document_frequency[token]))
                      for token in query_tokens & candidate_tokens[index])
        decision_words = case_match_tokens_ordered(" ".join([
            str(chosen.get("resumo", "")), str(chosen.get("motivo_relacao", "")),
            " ".join(str(q) for q in chosen.get("trechos_relacao", [])),
        ]))
        decision_bigrams = set(zip(decision_words, decision_words[1:]))
        overlap += 2.5 * len(query_bigrams & decision_bigrams)
        ranked.append((overlap, -index, decision, chosen))
    _, _, decision, source_alert = max(ranked, key=lambda item: (item[0], item[1]))
    simulated_alert = dict(source_alert)
    simulated_alert["caso"] = f"Simulação — {client_name}"
    simulated_alert["resumo"] = f"Exemplo demonstrativo: {source_alert.get('resumo', '')}"
    simulated_alert["motivo_relacao"] = "A decisão foi escolhida por semelhança com a descrição; isso não confirma relação jurídica direta com o caso."
    simulated_alert["posicao_cliente"] = "Favorabilidade a confirmar: este exemplo não avalia a posição do novo caso."
    simulated_alert["favorabilidade_a_confirmar"] = True
    simulated_alert["motivo_favorabilidade"] = "A favorabilidade do caso informado não foi analisada; este cartão é apenas um exemplo demonstrativo."
    simulated_alert["trecho_favorabilidade"] = ""
    notice = result_for_page({"alerts": [simulated_alert], "reviews": [],
                              "completed_count": 1, "selected_count": 1})["avisos"][0]
    return notice, simulated_alert


def case_match_tokens_ordered(text: str) -> list[str]:
    folded = unicodedata.normalize("NFKD", text.casefold())
    plain = "".join(char for char in folded if not unicodedata.combining(char))
    return [word for word in re.findall(r"[a-z0-9]{3,}", plain) if word not in CASE_MATCH_STOPWORDS]


def load_client_map() -> dict:
    try:
        data = json.loads(CLIENT_MAP_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def map_private_case_names(alerts: list[dict]) -> list[dict]:
    # Names are reattached locally, after the IA has returned its code-based analysis.
    mapping = load_client_map()
    display_names = {code: str(record.get("nome_cliente", "Cliente")) for code, record in mapping.items()}
    for alert in alerts:
        code = Path(str(alert.get("arquivo_caso", ""))).stem
        if code in display_names:
            alert["caso"] = f"Caso cadastrado — {display_names[code]}"
    return alerts


def result_for_page(result: dict) -> dict:
    notices = []
    for group in telos.group_alerts_by_decision(result.get("alerts", [])):
        first = group[0]
        if not all(telos.direct_alert_is_readable(alert) for alert in group):
            notices.append({
                "resumo": telos.UNREADABLE_OPINION,
                "resultado": "Não identificado no material",
                "metadata": telos.decision_metadata_text(first),
                "casos": [],
                "trechos": [],
                "link": first.get("link_oficial", ""),
                "somente_ementa": False,
            })
            continue
        notices.append({
            "resumo": first.get("resumo", "Resumo não disponível."),
            "resultado": first.get("resultado", "Não identificado no material"),
            "metadata": telos.decision_metadata_text(first),
            "casos": [
                {"titulo": alert.get("caso", "Caso do escritório"),
                 "favorabilidade": telos.alert_position_label(alert)}
                for alert in group
            ],
            "trechos": [
                {"caso": case_title, "texto": quote}
                for case_title, quote in telos.decision_evidence_by_case(group)
            ],
            "link": first.get("link_oficial", ""),
            "somente_ementa": any(alert.get("somente_ementa") for alert in group),
        })

    reviews = []
    for review in result.get("reviews", []):
        if not telos.review_pair_is_readable(review):
            reviews.append({
                "metadata": telos.decision_metadata_text(review),
                "casos": [],
                "divergencia": telos.UNREADABLE_OPINION,
                "link": review.get("link_oficial", ""),
            })
            continue
        items = telos.review_cases(review)
        reviews.append({
            "metadata": telos.decision_metadata_text(review),
            "casos": [
                {
                    "titulo": item["titulo"],
                    "parecer_1": telos.format_review_opinion(
                        "Parecer 1", item["parecer_1"], item["resultado_1"]
                    ),
                    "parecer_2": telos.format_review_opinion(
                        "Parecer 2", item["parecer_2"], item["resultado_2"]
                    ),
                }
                for item in items
            ],
            "divergencia": telos.review_disagreement_text(review, items),
            "link": review.get("link_oficial", ""),
        })
    return {
        "avisos": notices,
        "revisar": reviews,
        "concluidas": result.get("completed_count", 0),
        "selecionadas": result.get("selected_count", 0),
        "interrompida": bool(result.get("interrupted")),
        "email_enviado": result.get("email_sent"),
        "sem_impacto": result.get("sem_impacto", []),
    }


def decision_candidates(terms: list[str], saved: list[Path], area: str) -> list[Path]:
    found: list[Path] = []
    seen: set[str] = set()
    for path in [*saved, *sorted(telos.DECISIONS_DIR.iterdir())]:
        if not path.is_file() or path.suffix.lower() not in {".txt", ".pdf"}:
            continue
        if path.name in seen:
            continue
        seen.add(path.name)
        try:
            raw = telos.read_document(path)
        except Exception:
            continue
        match = re.search(r"(?m)^Busca:\s*(.*?)\s*$", raw)
        if match and match.group(1) in terms:
            found.append(path)
        elif area == "todas" and not match and not path.name.startswith("auto_"):
            found.append(path)

    completed = telos.load_analysis_state()
    return [
        path for path in found
        if telos.decision_fingerprint(path, telos.read_document(path)) not in completed
    ]


def progress_callback(stage: str, current: int, total: int) -> None:
    if stage == "searching":
        update_run(
            phase="searching",
            message=(f"Buscando decisões novas no TJSP ({current} de {total} termos)…"
                     if current else "Buscando decisões novas no TJSP…"),
            progress_current=current,
            progress_total=total,
        )
    elif stage == "analyzing":
        update_run(
            phase="analyzing",
            message=f"Analisando a decisão {current} de {total}…",
            progress_current=current,
            progress_total=total,
        )
    elif stage == "first_opinion":
        update_run(
            phase="first_opinion",
            message=f"Primeiro parecer — decisão {current} de {total}…",
            progress_current=current,
            progress_total=total,
        )
    elif stage == "second_opinion":
        update_run(
            phase="second_opinion",
            message=f"Segundo parecer — decisão {current} de {total}…",
            progress_current=current,
            progress_total=total,
        )
    elif stage == "parallel_opinions":
        update_run(
            phase="analyzing",
            message=f"Analisando decisões e emitindo segundos pareceres em paralelo ({current} de {total} análises)…",
            progress_current=current,
            progress_total=total,
        )
    elif stage == "sending_email":
        update_run(
            phase="sending_email",
            message="Enviando e-mail com os avisos…",
            progress_current=current,
            progress_total=total,
        )
    elif stage == "email_result":
        if current is True:
            message = "E-mail enviado. Finalizando a rodada…"
        elif current is False:
            message = "Não foi possível enviar o e-mail. Os avisos ficarão disponíveis nesta página."
        else:
            message = "E-mail não configurado; os avisos ficarão disponíveis nesta página."
        update_run(phase="saving", message=message)


def demo_round(area: str, decision_count: int, extra_email: str) -> None:
    global PENDING_EMAIL
    fixture = json.loads(DEMO_ROUND_FILE.read_text(encoding="utf-8"))
    all_decisions = fixture.get("decisions", [])
    decisions = [
        item for item in all_decisions
        if area == "todas" or item.get("area", "").lower() == {
            "imobiliario": "imobiliário",
            "empresarial": "empresarial",
            "bancario": "bancário",
        }.get(area)
    ][:decision_count]
    selected_files = {item.get("file") for item in decisions}
    alerts = [item for item in fixture.get("alerts", []) if item.get("decisao") in selected_files]
    reviews = [item for item in fixture.get("reviews", []) if item.get("decisao") in selected_files]
    no_impact_items = [item for item in fixture.get("sem_impacto", []) if item.get("decisao") in selected_files]
    total = len(decisions)
    update_run(phase="searching", message="Buscando decisões no TJSP…", progress_current=0, progress_total=total)
    time.sleep(2)
    update_run(phase="searching", message="Decisões selecionadas. Preparando a análise…", progress_current=0, progress_total=total)
    time.sleep(1.5)
    for index, item in enumerate(decisions, start=1):
        update_run(phase="analyzing", message=f"Analisando a decisão {index} de {total}…", progress_current=index - 1, progress_total=total)
        time.sleep(1.2)
        update_run(phase="second_opinion", message=f"Segundo parecer — decisão {index} de {total}…", progress_current=index - 1, progress_total=total)
        time.sleep(1.2)
        update_run(phase="analyzing", message=f"Análise concluída para a decisão {index} de {total}.", progress_current=index, progress_total=total)
        time.sleep(0.35)

    no_impact = [dict(item, metadata=telos.decision_metadata_text(item)) for item in no_impact_items]
    result = result_for_page({"alerts": alerts, "reviews": reviews,
                              "completed_count": total, "selected_count": total,
                              "sem_impacto": no_impact})
    area_label = {
        "imobiliario": "Direito Imobiliário",
        "empresarial": "Direito Empresarial",
        "bancario": "Direito Bancário",
        "todas": "Bancário, Imobiliário e Empresarial",
    }[area]
    result.update({"data_rodada": datetime.now().astimezone().isoformat(timespec="minutes"),
                   "area": area_label, "modo_demo": True,
                   "data_coleta": fixture.get("data_coleta")})
    PENDING_EMAIL = {"alerts": alerts, "reviews": reviews,
                     "completed_count": total, "selected_count": total,
                     "interrupted": False, "extra_recipients": extra_email or None,
                     "area": area}
    result["email_disponivel"] = False
    result["email_status"] = "none"
    write_latest_round(result)
    with STATE_LOCK:
        RUN_STATE["last_round"] = result
        RUN_STATE["email_status"] = "none"
        RUN_STATE["email_available"] = False
    update_run(phase="complete", message="Rodada concluída.",
               progress_current=total, progress_total=total)
    send_round_email_at_end(PENDING_EMAIL)


def run_round(area: str, decision_count: int, extra_email: str, demo: bool = False) -> None:
    global PENDING_EMAIL
    if DEMO_MODE:
        try:
            demo_round(area, decision_count, extra_email)
        except Exception as error:
            update_run(phase="error", message=f"A rodada não foi concluída ({type(error).__name__}). A última rodada continua disponível.")
        finally:
            update_run(running=False)
            RUN_LOCK.release()
        return

    original_decision_dir = telos.DECISIONS_DIR
    original_case_dir = telos.CASES_DIR
    original_case_display_names = telos.CASE_DISPLAY_NAMES.copy()
    original_max = telos.MAX_DECISIONS_PER_RUN
    provider, api_key, model = current_provider_settings()
    try:
        if provider not in {"openai", "gemini", "groq"} or not api_key:
            raise RuntimeError("O provedor de IA não está configurado.")
        terms = configured_terms(area)
        if not terms:
            raise RuntimeError("Não há termos de busca configurados para esta área.")

        period_end = datetime.now().date()
        period_start = period_end - timedelta(days=21)
        saved = telos.search_tjsp(
            progress_callback=progress_callback,
            search_terms_override=";".join(terms),
            date_start=period_start.strftime("%d/%m/%Y"),
            date_end=period_end.strftime("%d/%m/%Y"),
            pages=range(1, 4),
        )
        candidates = decision_candidates(terms, saved, area)[:decision_count]
        if not candidates:
            update_run(
                phase="complete",
                message="Nenhuma decisão nova pendente para esta seleção. A última rodada continua disponível.",
                running=False,
            )
            return

        with tempfile.TemporaryDirectory(prefix="telos_web_rodada_") as temporary:
            temporary_root = Path(temporary)
            decisions_dir = temporary_root / "decisoes"
            cases_dir = temporary_root / "casos"
            decisions_dir.mkdir()
            cases_dir.mkdir()
            for source in candidates:
                (decisions_dir / source.name).symlink_to(source)
            current_cases = cases_for_area(area)
            if not current_cases:
                raise RuntimeError("Não há casos cadastrados para esta área.")
            for source in current_cases:
                (cases_dir / source.name).symlink_to(source)

            telos.DECISIONS_DIR = decisions_dir
            telos.CASES_DIR = cases_dir
            telos.CASE_DISPLAY_NAMES = {
                code: str(record.get("nome_cliente", "Cliente"))
                for code, record in load_client_map().items()
            }
            result_holder: dict = {}
            def collect_result(result: dict) -> None:
                result_holder.update(result)

            telos.analyze_decisions(
                api_key,
                model,
                provider,
                max_decisions=decision_count,
                extra_recipients=extra_email or None,
                progress_callback=progress_callback,
                result_callback=collect_result,
                alert_transform=map_private_case_names,
                send_email_after=False,
            )

            if not result_holder:
                update_run(
                    phase="complete",
                    message="Não houve análise concluída nesta rodada. A última rodada continua disponível.",
                )
                return

            result = result_for_page(result_holder)
            result["data_rodada"] = datetime.now().astimezone().isoformat(timespec="minutes")
            result["area"] = {
                "imobiliario": "Direito Imobiliário",
                "empresarial": "Direito Empresarial",
                "bancario": "Direito Bancário",
                "todas": "Todas as áreas",
            }[area]
            result["termos"] = len(terms)
            result["modo_demo"] = False
            collection_times = []
            for path in candidates:
                stat = path.stat()
                collection_times.append(getattr(stat, "st_birthtime", stat.st_mtime))
            result["data_coleta"] = datetime.fromtimestamp(
                min(collection_times)
            ).astimezone().date().isoformat()
            PENDING_EMAIL = {"alerts": result_holder.get("alerts", []), "reviews": result_holder.get("reviews", []),
                             "completed_count": result_holder.get("completed_count", 0),
                             "selected_count": result_holder.get("selected_count", 0),
                             "interrupted": result_holder.get("interrupted", False),
                             "extra_recipients": extra_email or None}
            result["email_disponivel"] = False
            result["email_status"] = "none"
            if result["concluidas"] or RUN_STATE.get("last_round") is None:
                write_latest_round(result)
                with STATE_LOCK:
                    RUN_STATE["last_round"] = result
                    RUN_STATE["email_status"] = "none"
                    RUN_STATE["email_available"] = False
            if result["concluidas"] == 0 and RUN_STATE.get("last_round") is not None:
                update_run(phase="complete", message="Nenhuma decisão foi concluída. Mantive os avisos da rodada anterior.")
            elif result["interrompida"]:
                update_run(phase="complete", message="Rodada concluída parcialmente; veja os avisos e a seção de revisão.")
            else:
                update_run(phase="complete", message="Rodada concluída.")
            send_round_email_at_end(PENDING_EMAIL)
    except Exception as error:
        # Keep the previous completed results visible; never include configuration values here.
        update_run(phase="error", message=f"A rodada não foi concluída ({type(error).__name__}). A última rodada continua disponível.")
    finally:
        telos.DECISIONS_DIR = original_decision_dir
        telos.CASES_DIR = original_case_dir
        telos.CASE_DISPLAY_NAMES = original_case_display_names
        telos.MAX_DECISIONS_PER_RUN = original_max
        update_run(running=False)
        RUN_LOCK.release()


@app.after_request
def disable_caching(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/")
def home():
    with STATE_LOCK:
        initial_state = {
            "running": RUN_STATE["running"],
            "phase": RUN_STATE["phase"],
            "message": RUN_STATE["message"],
            "progress_current": RUN_STATE["progress_current"],
            "progress_total": RUN_STATE["progress_total"],
            "last_round": RUN_STATE["last_round"],
            "email_status": RUN_STATE.get("email_status", "none"),
            "email_available": RUN_STATE.get("email_available", False),
            "demo_mode": DEMO_MODE,
        }
    return render_template("index.html", initial_state=initial_state, demo_mode=DEMO_MODE)


@app.get("/casos")
def cases_page():
    local_only = request.remote_addr in {"127.0.0.1", "::1"}
    return render_template("casos.html", cases=case_list(), local_only=local_only,
                           hosted_simulation=TELOS_HOSPEDADO)


@app.get("/api/state")
def api_state():
    with STATE_LOCK:
        return jsonify({
            "running": RUN_STATE["running"],
            "phase": RUN_STATE["phase"],
            "message": RUN_STATE["message"],
            "progress_current": RUN_STATE["progress_current"],
            "progress_total": RUN_STATE["progress_total"],
            "last_round": RUN_STATE["last_round"],
            "email_status": RUN_STATE.get("email_status", "none"),
            "email_available": RUN_STATE.get("email_available", False),
            "demo_mode": DEMO_MODE,
        })


@app.post("/api/run")
def api_run():
    body = request.get_json(silent=True) or {}
    area = str(body.get("area", "todas" if DEMO_MODE else "imobiliario"))
    demo = DEMO_MODE
    if area not in CASE_AREAS:
        return jsonify({"error": "Escolha uma das áreas disponíveis."}), 400
    try:
        decision_count = int(body.get("decision_count", 5))
    except (TypeError, ValueError):
        return jsonify({"error": "Escolha de uma a cinco decisões."}), 400
    if decision_count < 1 or decision_count > 5:
        return jsonify({"error": "Escolha de uma a cinco decisões."}), 400
    extra_email = str(body.get("extra_email", "")).strip()
    if extra_email and not re.fullmatch(r"[^@\s,]+@[^@\s,]+\.[^@\s,]+", extra_email):
        return jsonify({"error": "Digite um endereço de e-mail válido."}), 400
    if not RUN_LOCK.acquire(blocking=False):
        return jsonify({"error": "Já há uma rodada em andamento."}), 409

    global PENDING_EMAIL
    PENDING_EMAIL = None
    with STATE_LOCK:
        RUN_STATE["email_available"] = False
        RUN_STATE["email_status"] = "none"
    update_run(
        running=True,
        phase="starting",
        message="Preparando a rodada…",
        progress_current=0,
        progress_total=0,
    )
    worker = threading.Thread(
        target=run_round,
        args=(area, decision_count, extra_email, demo),
        name="telos-round",
        daemon=True,
    )
    worker.start()
    return jsonify({"started": True}), 202


def email_success_message(payload: dict) -> str:
    if TELOS_HOSPEDADO:
        return "Avisos enviados para o seu e-mail."
    has_configured_recipients = bool(os.environ.get("GMAIL_RECIPIENT", "").strip())
    if payload.get("extra_recipients") and has_configured_recipients:
        return "Avisos enviados aos destinatários configurados e ao e-mail digitado."
    if payload.get("extra_recipients"):
        return "Avisos enviados para o e-mail digitado."
    return "Avisos enviados aos destinatários configurados."


def record_email_result(sent: bool | None, payload: dict, *, automatic: bool, error_message: str | None = None) -> None:
    status = "sent" if sent is True else "none" if sent is None else "failed"
    was_available = bool(RUN_STATE.get("email_available"))
    can_resend = sent is True or (was_available and not automatic)
    with STATE_LOCK:
        RUN_STATE["email_status"] = status
        RUN_STATE["email_available"] = can_resend
        last_round = RUN_STATE.get("last_round")
        if last_round:
            last_round["email_status"] = status
            last_round["email_enviado"] = sent
            last_round["email_disponivel"] = can_resend
            write_latest_round(last_round)
    if sent is True:
        message = email_success_message(payload)
    elif error_message:
        message = error_message
    elif sent is None:
        message = "Rodada concluída. Nenhum e-mail foi enviado porque não há destinatário configurado."
    else:
        message = "Não foi possível enviar os avisos por e-mail. Eles continuam disponíveis na página."
    update_run(phase="complete", message=message)


def send_round_email_payload(payload: dict, *, automatic: bool, rate_reserved: bool = False) -> bool | None:
    if TELOS_HOSPEDADO:
        recipient = str(payload.get("extra_recipients") or "").strip()
        existing_override = payload.get("recipients_override")
        if existing_override:
            recipient = str(existing_override[0]).strip()
        if not recipient:
            record_email_result(None, payload, automatic=automatic)
            return None
        if not rate_reserved:
            rate_error = reserve_hosted_email_slot()
            if rate_error:
                record_email_result(False, payload, automatic=automatic, error_message=rate_error)
                return False
        payload = dict(payload)
        payload["recipients_override"] = [recipient]
        payload["extra_recipients"] = None

    update_run(phase="sending_email", message="Enviando avisos por e-mail…")
    try:
        sent = telos.send_round_email(
            payload.get("alerts", []), payload.get("reviews", []),
            payload.get("completed_count", 0), payload.get("selected_count", 0),
            payload.get("interrupted", False), extra_recipients=payload.get("extra_recipients"),
            recipients_override=payload.get("recipients_override"),
            email_provider="brevo" if TELOS_HOSPEDADO else "gmail",
        )
        record_email_result(sent, payload, automatic=automatic)
        return sent
    except Exception as error:
        record_email_result(False, payload, automatic=automatic,
                            error_message=f"O envio falhou ({type(error).__name__}). Os avisos continuam na página.")
        return False


def send_round_email_at_end(payload: dict | None) -> None:
    if payload is None:
        return
    if TELOS_HOSPEDADO and not str(payload.get("extra_recipients") or "").strip():
        record_email_result(None, payload, automatic=True)
        return
    send_round_email_payload(payload, automatic=True)


def send_email_worker(payload: dict, *, rate_reserved: bool = False) -> None:
    try:
        send_round_email_payload(payload, automatic=False, rate_reserved=rate_reserved)
    finally:
        update_run(running=False)
        RUN_LOCK.release()


@app.post("/api/send-email")
def api_send_email():
    body = request.get_json(silent=True) or {}
    if PENDING_EMAIL is None or not RUN_STATE.get("email_available"):
        return jsonify({"error": "Não há avisos pendentes para enviar."}), 400
    payload = dict(PENDING_EMAIL)
    if TELOS_HOSPEDADO:
        recipient = str(body.get("extra_email", "")).strip()
        if not recipient or not re.fullmatch(r"[^@\s,]+@[^@\s,]+\.[^@\s,]+", recipient):
            return jsonify({"error": "Digite um e-mail válido para receber os avisos."}), 400
        payload["recipients_override"] = [recipient]
        payload["extra_recipients"] = None
    elif body.get("extra_email"):
        recipient = str(body.get("extra_email", "")).strip()
        if not re.fullmatch(r"[^@\s,]+@[^@\s,]+\.[^@\s,]+", recipient):
            return jsonify({"error": "Digite um endereço de e-mail válido."}), 400
        payload["extra_recipients"] = recipient
    if not RUN_LOCK.acquire(blocking=False):
        return jsonify({"error": "Aguarde a atividade atual terminar."}), 409
    rate_error = reserve_hosted_email_slot()
    if rate_error:
        RUN_LOCK.release()
        return jsonify({"error": rate_error}), 429
    update_run(running=True, phase="sending_email", message="Preparando o envio do e-mail…")
    threading.Thread(target=send_email_worker, kwargs={"payload": payload, "rate_reserved": True}, name="telos-email", daemon=True).start()
    return jsonify({"started": True}), 202


@app.post("/api/cases")
def api_create_case():
    if not TELOS_HOSPEDADO and request.remote_addr not in {"127.0.0.1", "::1"}:
        return jsonify({"error": "Não foi possível cadastrar este caso."}), 403
    body = request.get_json(silent=True) or {}
    kind = str(body.get("kind", "")).strip().lower()
    name = str(body.get("client_name", "")).strip()
    description = str(body.get("description", "")).strip()
    area = str(body.get("area", "")).strip().lower()
    if kind not in {"contrato", "processo"}:
        return jsonify({"error": "Escolha contrato ou processo."}), 400
    if not name or len(name) > 160 or not description or len(description) > 4000:
        return jsonify({"error": "Preencha o nome do cliente e uma descrição com até 4.000 caracteres."}), 400
    if area not in {"imobiliario", "empresarial", "bancario"}:
        return jsonify({"error": "Escolha uma área do Direito."}), 400
    email = str(body.get("email", "")).strip()
    if TELOS_HOSPEDADO:
        if email and not re.fullmatch(r"[^@\s,]+@[^@\s,]+\.[^@\s,]+", email):
            return jsonify({"error": "Digite um e-mail válido ou deixe o campo vazio."}), 400
        example = demo_case_example(description, name, area)
        if example is None:
            return jsonify({"error": "Não encontramos uma decisão de demonstração adequada para essa área."}), 404
        notice, email_alert = example
        email_sent = None
        email_message = ""
        if email:
            rate_error = reserve_hosted_email_slot()
            if rate_error:
                email_message = rate_error
            else:
                email_sent = telos.send_round_email(
                    [email_alert], [], 1, 1, False,
                    recipients_override=[email], email_provider="brevo",
                )
                email_message = "O exemplo foi enviado para o e-mail informado." if email_sent is True else (
                    "Não foi possível enviar o e-mail, mas o exemplo está disponível nesta tela."
                )
        return jsonify({
            "simulation": True,
            "message": "Este exemplo usa a decisão de demonstração mais parecida com a descrição. Não é uma análise do seu caso.",
            "notice": notice,
            "email_sent": email_sent,
            "email_message": email_message,
        }), 200

    import secrets
    code = "caso-" + secrets.token_hex(5)
    case_folder = telos.CASES_DIR / "cadastrados"
    case_folder.mkdir(parents=True, exist_ok=True)
    case_path = case_folder / f"{code}.txt"
    case_path.write_text(
        f"Código: {code}\nTipo: {kind}\nÁrea: {area}\nDescrição:\n{description}\n",
        encoding="utf-8",
    )
    mapping = load_client_map()
    mapping[code] = {"nome_cliente": name, "tipo": kind, "area": area}
    CLIENT_MAP_FILE.parent.mkdir(parents=True, exist_ok=True)
    CLIENT_MAP_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return jsonify({"created": True, "message": "Caso cadastrado. Ele entra na próxima rodada."}), 201


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, threaded=True, debug=False)
