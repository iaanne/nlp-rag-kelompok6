"""Chatbot RAG EWS (terminal, tanpa n8n).

Jalankan dari root repo: python -m chatbot.chat_cli
Perintah: tanya biasa -> RAG | /check ... -> skor EWS | exit/quit -> keluar.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.router import route

BANNER = ("Chatbot RAG EWS (edukasi, bukan alat klinis).\n"
          "Ketik pertanyaan, /check HR=125 SYS=88 RR=29 SPO2=90 T=39.5 AVPU=V O2=oxygen, atau exit.\n")


def render(res: dict) -> str:
    if res["type"] == "ews":
        lines = [f"EWS={res['total']} [{res['band']}]"]
        lines += [f"  {k}: {s}" for k, s in res["parts"].items()]
        lines.append(f"Advice: {res['advice']}")
        return "\n".join(lines)
    out = res["answer"]
    if res.get("citations"):
        out += "\n[Rujukan: " + ", ".join(res["citations"]) + "]"
    return out


def main() -> None:
    print(BANNER)
    while True:
        try:
            q = input("kamu> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbubye.")
            break
        if q.lower() in {"exit", "quit", ":q"}:
            print("bubye.")
            break
        if not q:
            continue
        print("bot> " + render(route(q)) + "\n")


if __name__ == "__main__":
    main()
