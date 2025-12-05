import os

bind = "127.0.0.1:8001"
workers = 2
worker_class = "sync"
timeout = 120

# VPS環境用のBASE_PATH設定
# ローカル環境では空文字列として動作する
os.environ['BASE_PATH'] = '/tournament'
