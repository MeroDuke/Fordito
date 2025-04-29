import qbittorrentapi
import configparser
import os

class QBittorrentClient:
    def __init__(self, host="localhost", port=8080, username="admin", password="adminadmin"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = None

    def login(self):
        self.client = qbittorrentapi.Client(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password
        )
        self.client.auth_log_in()

    def get_torrents_info(self):
        if self.client is None:
            raise RuntimeError("Client is not connected. Call login() first.")
        return self.client.torrents_info()

    def add_torrent_by_url(self, torrent_url, save_path):
        if self.client is None:
            raise RuntimeError("Client is not connected. Call login() first.")
        self.client.torrents_add(urls=torrent_url, save_path=save_path)

    def get_torrent_status_by_hash(self, torrent_hash):
        if self.client is None:
            raise RuntimeError("Client is not connected. Call login() first.")
        torrents = self.client.torrents_info(torrent_hashes=torrent_hash)
        if torrents:
            return torrents[0]  # Az első torrent a hash alapján
        return None

    def delete_all_torrents(self, delete_files=True):
        if self.client is None:
            raise RuntimeError("Client is not connected. Call login() first.")
        self.client.torrents_delete(delete_files=delete_files, hashes="all")

def create_client_from_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")
    host = config["QBITTORRENT"].get("HOST", "localhost")
    port = config["QBITTORRENT"].getint("PORT", 8080)
    username = config["QBITTORRENT"].get("USERNAME", "admin")
    password = config["QBITTORRENT"].get("PASSWORD", "adminadmin")

    client = QBittorrentClient(host=host, port=port, username=username, password=password)
    client.login()
    return client
