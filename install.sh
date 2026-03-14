#!/usr/bin/env bash
# =============================================================================
# install.sh — Установщик Telegram Circle Bot
# Устанавливает бота в /opt/circlebot, создаёт команду circlebot
# Поддерживаемые ОС: Ubuntu/Debian
# =============================================================================

set -e

# ── Цвета для вывода ──────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

INSTALL_DIR="/opt/circlebot"
REPO_URL="https://github.com/zmey93/telegram-circle-bot.git"
CMD_PATH="/usr/local/bin/circlebot"

log_info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()  { echo -e "\n${BLUE}══════════════════════════════════════${NC}"; echo -e "${BLUE}  $1${NC}"; echo -e "${BLUE}══════════════════════════════════════${NC}"; }

# ── Проверка прав root ───────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    log_error "Скрипт должен запускаться от root. Используй: sudo bash install.sh"
    exit 1
fi

# ── Проверка Docker ──────────────────────────────────────────────────────────
log_step "Проверка зависимостей"

if ! command -v docker &>/dev/null; then
    log_warn "Docker не найден. Устанавливаю..."
    apt-get update -qq
    apt-get install -y ca-certificates curl gnupg
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -qq
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    log_info "Docker установлен!"
else
    log_info "Docker найден: $(docker --version)"
fi

if ! docker compose version &>/dev/null; then
    log_error "docker compose plugin не найден. Установи Docker актуальной версии."
    exit 1
fi

if ! command -v git &>/dev/null; then
    log_warn "git не найден. Устанавливаю..."
    apt-get install -y git
fi

# ── Клонирование репозитория ─────────────────────────────────────────────────
log_step "Установка в $INSTALL_DIR"

if [[ -d "$INSTALL_DIR" ]]; then
    log_warn "Директория $INSTALL_DIR уже существует. Обновляю код..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    log_info "Репозиторий клонирован в $INSTALL_DIR"
fi

mkdir -p "$INSTALL_DIR/temp"
chmod 755 "$INSTALL_DIR/temp"

# ── Настройка .env ───────────────────────────────────────────────────────────
log_step "Настройка токена"

if [[ ! -f "$INSTALL_DIR/.env" ]]; then
    echo ""
    read -rp "  Введи BOT_TOKEN от @BotFather: " BOT_TOKEN_INPUT
    if [[ -z "$BOT_TOKEN_INPUT" ]]; then
        log_error "Токен не может быть пустым!"
        exit 1
    fi
    echo "BOT_TOKEN=${BOT_TOKEN_INPUT}" > "$INSTALL_DIR/.env"
    chmod 600 "$INSTALL_DIR/.env"
    log_info ".env создан"
else
    log_info ".env уже существует, пропускаю"
fi

# ── Установка команды circlebot ──────────────────────────────────────────────
log_step "Создание команды circlebot"

cat > "$CMD_PATH" << 'EOF'
#!/usr/bin/env bash
# Команда управления Telegram Circle Bot
INSTALL_DIR="/opt/circlebot"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_help() {
    echo -e ""
    echo -e "${BLUE}  🎥 Telegram Circle Bot — управление${NC}"
    echo -e ""
    echo -e "  Использование: ${GREEN}circlebot <команда>${NC}"
    echo -e ""
    echo -e "  Команды:"
    echo -e "    ${GREEN}start${NC}      — Запустить бота"
    echo -e "    ${GREEN}stop${NC}       — Остановить бота"
    echo -e "    ${GREEN}restart${NC}    — Перезапустить бота"
    echo -e "    ${GREEN}update${NC}     — Обновить бота (git pull + пересборка)"
    echo -e "    ${GREEN}status${NC}     — Статус контейнера"
    echo -e "    ${GREEN}logs${NC}       — Показать логи (Ctrl+C для выхода)"
    echo -e "    ${GREEN}install${NC}    — Первичная установка (запросит токен)"
    echo -e "    ${GREEN}uninstall${NC}  — Удалить бота и все файлы"
    echo -e ""
}

check_dir() {
    if [[ ! -d "$INSTALL_DIR" ]]; then
        echo -e "${RED}[ERROR]${NC} Бот не установлен. Запусти: sudo circlebot install"
        exit 1
    fi
}

case "$1" in
    start)
        check_dir
        echo -e "${GREEN}[START]${NC} Запуск Circle Bot..."
        cd "$INSTALL_DIR"
        docker compose up -d --build
        echo -e "${GREEN}[OK]${NC} Бот запущен!"
        ;;
    stop)
        check_dir
        echo -e "${YELLOW}[STOP]${NC} Остановка Circle Bot..."
        cd "$INSTALL_DIR"
        docker compose down
        echo -e "${YELLOW}[OK]${NC} Бот остановлен."
        ;;
    restart)
        check_dir
        echo -e "${YELLOW}[RESTART]${NC} Перезапуск Circle Bot..."
        cd "$INSTALL_DIR"
        docker compose restart
        echo -e "${GREEN}[OK]${NC} Бот перезапущен!"
        ;;
    update)
        check_dir
        echo -e "${BLUE}[UPDATE]${NC} Обновление Circle Bot..."
        cd "$INSTALL_DIR"
        echo -e "  → Получение последних изменений из git..."
        git pull origin main
        echo -e "  → Остановка контейнера..."
        docker compose down
        echo -e "  → Пересборка и запуск..."
        docker compose up -d --build
        echo -e "${GREEN}[OK]${NC} Бот обновлён и перезапущен!"
        ;;
    status)
        check_dir
        echo -e "${BLUE}[STATUS]${NC} Статус Circle Bot:"
        cd "$INSTALL_DIR"
        docker compose ps
        ;;
    logs)
        check_dir
        echo -e "${BLUE}[LOGS]${NC} Логи Circle Bot (Ctrl+C для выхода):"
        cd "$INSTALL_DIR"
        docker compose logs -f bot
        ;;
    install)
        if [[ $EUID -ne 0 ]]; then
            echo -e "${RED}[ERROR]${NC} Требуются права root. Используй: sudo circlebot install"
            exit 1
        fi
        bash /opt/circlebot/install.sh
        ;;
    uninstall)
        if [[ $EUID -ne 0 ]]; then
            echo -e "${RED}[ERROR]${NC} Требуются права root. Используй: sudo circlebot uninstall"
            exit 1
        fi
        echo -e "${RED}[UNINSTALL]${NC} Удаление Circle Bot..."
        cd "$INSTALL_DIR" 2>/dev/null && docker compose down 2>/dev/null || true
        rm -rf "$INSTALL_DIR"
        rm -f /usr/local/bin/circlebot
        echo -e "${GREEN}[OK]${NC} Бот полностью удалён."
        ;;
    *)
        show_help
        ;;
esac
EOF

chmod +x "$CMD_PATH"
log_info "Команда circlebot установлена в $CMD_PATH"

# ── Сборка и запуск ──────────────────────────────────────────────────────────
log_step "Сборка и запуск Docker контейнера"

cd "$INSTALL_DIR"
docker compose down 2>/dev/null || true
docker compose up -d --build

# ── Финал ────────────────────────────────────────────────────────────────────
log_step "✅ Установка завершена!"
echo ""
echo -e "  Директория:  ${GREEN}$INSTALL_DIR${NC}"
echo -e "  Команда:     ${GREEN}circlebot <start|stop|restart|update|status|logs>${NC}"
echo ""
echo -e "  Примеры:"
echo -e "    ${YELLOW}circlebot status${NC}   — посмотреть статус"
echo -e "    ${YELLOW}circlebot logs${NC}     — смотреть логи"
echo -e "    ${YELLOW}circlebot update${NC}   — обновить до последней версии"
echo ""
