import json
import os


class TokenAPI:
    def __init__(self, file_path):
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

    def update_tokens(self, player_id, nr_tokens):
        data = self._read_data()

        current_tokens = data.get(player_id, 0)
        data[player_id] = current_tokens + nr_tokens

        self._write_data(data)

    def set_tokens(self, player_id, nr_tokens):
        data = self._read_data()

        data[player_id] = nr_tokens

        self._write_data(data)

    def get_tokens(self, player_id):
        data = self._read_data()

        return data.get(player_id, 0)

    def get_players(self):
        data = self._read_data()

        return list(data.keys())

    def has_player(self, player_id):
        return player_id in self.get_players()
