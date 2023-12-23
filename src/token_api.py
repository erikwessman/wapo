import json
import os


class TokenAPI:
    def __init__(self, file_path: str):
        self.file_path = file_path

        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                json.dump({}, file)

    def _read_data(self):
        with open(self.file_path, "r") as file:
            return json.load(file)

    def _write_data(self, data):
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)

    def update_tokens(self, player_id: int, nr_tokens: int):
        data = self._read_data()

        player_id_str = str(player_id)
        current_tokens = data.get(player_id_str, 0)
        data[player_id] = current_tokens + nr_tokens

        self._write_data(data)

    def set_tokens(self, player_id: int, nr_tokens: int):
        data = self._read_data()

        player_id_str = str(player_id)
        data[player_id_str] = nr_tokens

        self._write_data(data)

    def get_tokens(self, player_id: int):
        data = self._read_data()

        player_id_str = str(player_id)
        return data.get(player_id_str, 0)

    def get_players(self):
        data = self._read_data()

        return list(data.keys())

    def has_player(self, player_id: str) -> bool:
        return str(player_id) in self.get_players()
