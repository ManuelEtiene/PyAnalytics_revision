#!/usr/bin/env bash
# Sobe o portal Streamlit do PyAnalytics.
# Uso: ./run.sh   (sem sudo)
set -euo pipefail

PORTA="${PORTA:-8501}"
URL="http://localhost:${PORTA}"

# Pasta streamlit/ (onde este script vive).
dir_script() {
  cd "$(dirname "${BASH_SOURCE[0]}")"
  pwd
}

# Raiz do repositório (contém requirements.txt e data/).
raiz_repo() {
  cd "$(dir_script)/.."
  pwd
}

# Streamlit não precisa de root; sudo dispara o onboarding no /root.
relancar_sem_sudo() {
  if [[ "$(id -u)" -ne 0 || -z "${SUDO_USER:-}" ]]; then
    return 0
  fi
  echo "Não use sudo. Relançando como ${SUDO_USER}..."
  exec sudo -u "$SUDO_USER" -H bash "$(dir_script)/run.sh" "$@"
}

# Cria .venv e instala deps só se o Streamlit ainda não estiver no ambiente.
garantir_venv() {
  local raiz="$1"
  local venv="$raiz/.venv"
  if [[ -x "$venv/bin/streamlit" ]]; then
    return 0
  fi
  python3 -m venv "$venv"
  "$venv/bin/pip" install -r "$raiz/requirements.txt"
}

# Sobe o app sem pedir e-mail (headless) e mostra o link.
subir_portal() {
  local raiz="$1"
  cd "$raiz"
  echo "Portal: ${URL}"
  exec "$raiz/.venv/bin/streamlit" run streamlit/app.py \
    --server.headless true \
    --browser.gatherUsageStats false \
    --server.port "$PORTA"
}

main() {
  local raiz
  relancar_sem_sudo "$@"
  raiz="$(raiz_repo)"
  garantir_venv "$raiz"
  subir_portal "$raiz"
}

main "$@"
