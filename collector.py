import base64
import re
import urllib.request

# Список источников (Telegram-каналы, открытые подписки, Gist)
SOURCES = [
    "https://t.me/s/v2ray_free_conf",
    "https://t.me/s/FreeV2rayConfig",
    "https://t.me/s/v2rayKng",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/xray/base64",
]

# Регулярное выражение для поиска VPN-ключей
CONFIG_PATTERN = re.compile(
    r"(vless|vmess|ss|trojan|hysteria2|hy2)://[^\s<>\"']+"
)


def fetch_and_extract():
    all_configs = set()

    for url in SOURCES:
        try:

            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode("utf-8", errors="ignore")

                # Если контент в Base64, пробуем декодировать
                try:
                    decoded = base64.b64decode(content).decode(
                        "utf-8", errors="ignore"
                    )
                    content += "\n" + decoded
                except Exception:
                    pass

                # Находим все ключи
                matches = CONFIG_PATTERN.findall(content)
                found = re.findall(CONFIG_PATTERN, content)
                # Ищем полные совпадения
                for line in content.splitlines():
                    for match in CONFIG_PATTERN.finditer(line):
                        all_configs.add(match.group(0))

                print(f"[+] Успешно обработан источник: {url}")
        except Exception as e:
            print(f"[-] Ошибка при загрузке {url}: {e}")

    return list(all_configs)


def main():
    configs = fetch_and_extract()
    print(f"Всего найдено уникальных ключей: {len(configs)}")

    if not configs:
        print("Ключи не найдены, пропуск обновления.")
        return

    # Объединяем ключи и кодируем в Base64 для подписки
    raw_text = "\n".join(configs)
    b64_output = base64.b64encode(raw_text.encode("utf-8")).decode("utf-8")

    # Сохраняем в файл output/v2ray-base64.txt
    with open("output/v2ray-base64.txt", "w", encoding="utf-8") as f:
        f.write(b64_output)

    print("[SUCCESS] Файл output/v2ray-base64.txt успешно обновлен!")


if __name__ == "__main__":
    main()
