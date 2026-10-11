import base64
import socket
import urllib.parse
import urllib.request
import time

# Рабочие и свежие источники
SOURCES = [
    # Основные рабочие подписки от yebekhe, с которых всё отлично летает
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/base64/mix",
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
    "https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/output/v2ray-base64.txt",
    
    # Файлы по странам
    "https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/output/country/DE.txt",
    "https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/output/country/NL.txt",
    "https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/output/country/FI.txt",
    "https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/output/country/US.txt",
    # Дополнительные проверенные сборки
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub1.txt",
    "https://t.me/s/v2ray_vpn_ir",
    "https://t.me/s/v2ray_free_conf",
]




def get_host_ping(host, port, timeout=2):
    """Возвращает пинг в миллисекундах или None, если сервер не отвечает"""
    start_time = time.time()
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return int((time.time() - start_time) * 1000)
    except Exception:
        return None


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

# Замер пинга и отбор самых быстрых серверов
    tested_configs = []
    
    for cfg in raw_configs:
        host, port = parse_host_port(cfg)
        if host and port:
            ping = get_host_ping(host, port)
            if ping is not None:
                tested_configs.append((ping, cfg))
                print(f"[+] {host}:{port} — ping: {ping} ms")
    
    # Сортируем от наименьшего пинга к наибольшему
    tested_configs.sort(key=lambda x: x[0])
    
    # Забираем только ТОП-100 самых быстрых
    working_configs = [cfg for ping, cfg in tested_configs[:100]]
    
    print(f"\n[!] Отобрано {len(working_configs)} самых быстрых серверов (из {len(tested_configs)} доступных)")
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
