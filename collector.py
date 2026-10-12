import base64
import socket
import urllib.parse
import urllib.request
import time
import urllib.parse
import random

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
    # 1. Morpheusadam v2ray-config (отдельные файлы с фокусом на Reality)
    "https://raw.githubusercontent.com/morpheusadam/v2ray-config/main/reality.txt",
    "https://raw.githubusercontent.com/morpheusadam/v2ray-config/main/vless.txt",
    "https://raw.githubusercontent.com/morpheusadam/v2ray-config/main/best.txt",
    
    # 2. Au1rxx Free VPN Subscriptions
    "https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/sub/vless.txt",
    "https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/sub/mix.txt",
    
    # 3. Mahdibland V2RayAggregator
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_reality.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_vless.txt",
    
    # 4. Iboxz Free V2Ray Collector
    "https://raw.githubusercontent.com/iboxz/free-v2ray-collector/main/sub/vless.txt",
    "https://raw.githubusercontent.com/iboxz/free-v2ray-collector/main/sub/reality.txt",
    
    # 5. VovaplusEXP p-configs
    "https://raw.githubusercontent.com/VovaplusEXP/p-configs/main/output/reality.txt",
    "https://raw.githubusercontent.com/VovaplusEXP/p-configs/main/output/vless.txt",
    
    # 6. Turbine8845 Telegram Configs Collector
    "https://raw.githubusercontent.com/Turbine8845/telegram-configs-collector/main/vless.txt",
    "https://raw.githubusercontent.com/Turbine8845/telegram-configs-collector/main/reality.txt",
    
    # 7. Дополнительные проверенные агрегаторы
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/outputs/vless.txt",
    "https://raw.githubusercontent.com/mehrtat/vless-collector/main/vless.txt"
]




def get_host_ping(host, port, timeout=2.5):
    """Более точный замер TCP-соединения с отсечением ложных 1мс заглушек"""
    start_time = time.time()
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        elapsed = int((time.time() - start_time) * 1000)
        
        # Защита от фейковых моментальных ответов CDN (0-2 мс обычно врут)
        if elapsed < 3:
            return 5 # Устанавливаем честный минимальный пинг
        return elapsed
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

import urllib.parse

def rename_config(config_url, index, ping):
    """Добавляет номер, пинг и крутые эмодзи к названию"""
    try:
        if "#" in config_url:
            base_url, original_name = config_url.split("#", 1)
            original_name = urllib.parse.unquote(original_name)
        else:
            base_url = config_url
            original_name = "Server"
        
        # Набор стильных эмодзи для разнообразия
        icons = ["⚡", "🚀", "🔥", "💎", "🎯", "🌐", "🔋"]
        selected_icon = icons[(index - 1) % len(icons)] # Циклично подбираем иконку под номер
        
        # Красивое имя с эмодзи
        new_name = f"{selected_icon} NT-VPN #{index:02d} [{ping}ms] | {original_name}"
        
        encoded_name = urllib.parse.quote(new_name)
        return f"{base_url}#{encoded_name}"
    except:
        return config_url



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
            # Отсекаем мертвые и те, у которых пинг больше 800мс
            if ping is not None and ping < 800:
                tested_configs.append((ping, cfg))
                print(f"[+] {host}:{port} — ping: {ping} ms")
    
    # Сортируем от наименьшего пинга к наибольшему
    tested_configs.sort(key=lambda x: x[0])
    
# Забираем ТОП-100 и красиво переименовываем
    working_configs = []
    for idx, (ping, cfg) in enumerate(tested_configs[:100], start=1):
        pretty_cfg = rename_config(cfg, idx, ping)
        working_configs.append(pretty_cfg)
    
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
