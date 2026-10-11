import base64
import socket
import urllib.parse
import urllib.request

# Рабочие и свежие источники
SOURCES = [
    # Основные рабочие подписки от yebekhe, с которых всё отлично летает
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/base64/mix",
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
    # Дополнительные проверенные сборки
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub1.txt",
    "https://t.me/s/v2ray_vpn_ir",
    "https://t.me/s/v2ray_free_conf",
]


def check_host_alive(host, port, timeout=2):
    """Быстрая проверка доступности порта сервера"""
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True
    except Exception:
        return False


def parse_host_port(config_url):
    """Извлекает хост и порт из ссылки VLESS/VMess/SS"""
    try:
        parsed = urllib.parse.urlparse(config_url)
        host = parsed.hostname
        port = parsed.port or 443
        if host:
            return host, port
    except Exception:
        pass
    return None, None


def fetch_and_filter():
    raw_configs = set()

    for url in SOURCES:
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode("utf-8", errors="ignore")

                # Пробуем декодировать Base64, если источник зашифрован
                try:
                    decoded = base64.b64decode(content).decode(
                        "utf-8", errors="ignore"
                    )
                    content += "\n" + decoded
                except Exception:
                    pass

                for line in content.splitlines():
                    line = line.strip()
                    if any(
                        line.startswith(proto)
                        for proto in [
                            "vless://",
                            "vmess://",
                            "ss://",
                            "trojan://",
                        ]
                    ):
                        raw_configs.add(line)
        except Exception as e:
            print(f"[-] Ошибка источника {url}: {e}")

    print(f"[i] Всего найдено кандидатов: {len(raw_configs)}")

    # Фильтрация только живых серверов
    working_configs = []
    for cfg in raw_configs:
        host, port = parse_host_port(cfg)
        if host and port:
            if check_host_alive(host, port):
                working_configs.append(cfg)
                print(f"[+] Рабочий сервер: {host}:{port}")

    return working_configs


def main():
    configs = fetch_and_filter()
    print(f"\n[SUMMARY] Отфильтровано рабочих серверов: {len(configs)}")

    if not configs:
        print("[!] Нет рабочих серверов для сохранения.")
        return

    raw_text = "\n".join(configs)
    b64_output = base64.b64encode(raw_text.encode("utf-8")).decode("utf-8")

    with open("output/v2ray-base64.txt", "w", encoding="utf-8") as f:
        f.write(b64_output)

    print("[SUCCESS] Обновлено только живыми прокси!")


if __name__ == "__main__":
    main()
