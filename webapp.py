"""Interface web simples para apresentar o Telos."""

from __future__ import annotations

import hmac
import json
import os
import re
import tempfile
import threading
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request

import telos


telos.load_env_file()
ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("TELOS_DATA_DIR", ROOT / ".telos_web_data"))
LATEST_FILE = DATA_DIR / "ultima_rodada.json"
CASE_AREAS = {
    "imobiliario": range(1, 8),
    "empresarial": range(8, 13),
    "todas": range(1, 13),
}
AREA_TERM_ENV = {
    "imobiliario": "TJSP_SEARCH_TERMS_IMOBILIARIO",
    "empresarial": "TJSP_SEARCH_TERMS_EMPRESARIAL",
}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
RUN_LOCK = threading.Lock()
STATE_LOCK = threading.Lock()


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


def current_provider_settings() -> tuple[str, str, str]:
    provider = os.environ.get("AI_PROVIDER", "gemini").strip().lower() or "gemini"
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
    return [
        path for path in sorted(telos.CASES_DIR.glob("*.txt"))
        if path.is_file() and case_number(path) in allowed
    ]


def case_list() -> list[dict]:
    items = []
    for path in sorted(telos.CASES_DIR.glob("*.txt")):
        try:
            content = telos.read_document(path)
        except (OSError, RuntimeError):
            continue
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        number = case_number(path)
        area = "Imobiliário" if number in CASE_AREAS["imobiliario"] else (
            "Empresarial" if number in CASE_AREAS["empresarial"] else "Caso de controle"
        )
        items.append({
            "titulo": telos.email_case_title(path.name),
            "descricao": " ".join(lines[1:]) if len(lines) > 1 else "Descrição não informada.",
            "area": area,
        })
    return items


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


def run_round(area: str, decision_count: int, extra_email: str) -> None:
    original_decision_dir = telos.DECISIONS_DIR
    original_case_dir = telos.CASES_DIR
    original_max = telos.MAX_DECISIONS_PER_RUN
    provider, api_key, model = current_provider_settings()
    try:
        if provider not in {"gemini", "groq"} or not api_key:
            raise RuntimeError("O provedor de IA não está configurado.")
        terms = configured_terms(area)
        if not terms:
            raise RuntimeError("Não há termos de busca configurados para esta área.")

        saved = telos.search_tjsp(
            progress_callback=progress_callback,
            search_terms_override=";".join(terms),
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
                "todas": "Todas as áreas",
            }[area]
            result["termos"] = len(terms)
            if result["concluidas"] or RUN_STATE.get("last_round") is None:
                write_latest_round(result)
                with STATE_LOCK:
                    RUN_STATE["last_round"] = result
            if result["concluidas"] == 0 and RUN_STATE.get("last_round") is not None:
                update_run(phase="complete", message="Nenhuma decisão foi concluída. Mantive os avisos da rodada anterior.")
            elif result["interrompida"]:
                update_run(phase="complete", message="Rodada concluída parcialmente; veja os avisos e a seção de revisão.")
            else:
                update_run(phase="complete", message="Rodada concluída.")
    except Exception as error:
        # Keep the previous completed results visible; never include configuration values here.
        update_run(phase="error", message=f"A rodada não foi concluída ({type(error).__name__}). A última rodada continua disponível.")
    finally:
        telos.DECISIONS_DIR = original_decision_dir
        telos.CASES_DIR = original_case_dir
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
        }
    return render_template("index.html", initial_state=initial_state)


@app.get("/casos")
def cases_page():
    return render_template("casos.html", cases=case_list())


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
        })


@app.post("/api/run")
def api_run():
    body = request.get_json(silent=True) or {}
    access_code = str(body.get("access_code", ""))
    configured_code = os.environ.get("TELOS_ACCESS_CODE", "")
    if configured_code and not hmac.compare_digest(access_code, configured_code):
        return jsonify({"error": "Código de acesso incorreto."}), 403
    hosted_access_required = (
        os.environ.get("TELOS_REQUIRE_ACCESS_CODE", "").strip().lower() == "true"
        or bool(os.environ.get("RENDER"))
    )
    if not configured_code and hosted_access_required:
        return jsonify({"error": "O acesso desta página ainda não foi configurado."}), 403

    area = str(body.get("area", "imobiliario"))
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

    update_run(
        running=True,
        phase="starting",
        message="Preparando a rodada…",
        progress_current=0,
        progress_total=0,
    )
    worker = threading.Thread(
        target=run_round,
        args=(area, decision_count, extra_email),
        name="telos-round",
        daemon=True,
    )
    worker.start()
    return jsonify({"started": True}), 202


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, threaded=True, debug=False)
