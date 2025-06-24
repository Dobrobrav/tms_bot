def make_pretty_json_in_telegram(json_str: str) -> str:
    return ('```json\n'
            f'{json_str}\n'
            '```')