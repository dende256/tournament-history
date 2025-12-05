# 環境別設定ガイド

## 概要

`BASE_PATH` 環境変数を使用して、ローカル環境とVPS環境で異なるルーティングに対応します。

## ローカル環境

**設定不要** - デフォルトで `BASE_PATH=""` (空文字列) が使用されます。

```bash
cd /home/ike/tournament
source venv/bin/activate
python app.py
```

アクセスURL:
- `http://localhost:5001/`
- `http://localhost:5001/add`
- `http://localhost:5001/edit/<id>`

## VPS環境

### Supervisor設定の更新

`/etc/supervisor/conf.d/tournament-app.conf` を編集：

```bash
sudo nano /etc/supervisor/conf.d/tournament-app.conf
```

`environment` 行を追加：

```ini
[program:tournament-app]
command=/home/ike/tournament/venv/bin/gunicorn -c gunicorn_config.py app:app
directory=/home/ike/tournament
user=ike
autostart=true
autorestart=true
stderr_logfile=/var/log/tournament-app.err.log
stdout_logfile=/var/log/tournament-app.out.log
environment=BASE_PATH="/tournament"
```

### 設定の反映

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl stop tournament-app
sudo supervisorctl start tournament-app
sudo supervisorctl status tournament-app
```

### 確認

```bash
# 環境変数が設定されているか確認
sudo supervisorctl status tournament-app
cat /var/log/tournament-app.out.log
```

アクセスURL:
- `https://your-domain.example.com/tournament/`
- `https://your-domain.example.com/tournament/add`
- `https://your-domain.example.com/tournament/edit/<id>`

## トラブルシューティング

### fetch URLが404エラー

環境変数が正しく設定されていない可能性があります。

```bash
# Supervisor設定を確認
sudo cat /etc/supervisor/conf.d/tournament-app.conf | grep environment

# 再起動
sudo supervisorctl stop tournament-app
sudo supervisorctl start tournament-app
```

### テンプレートでbase_pathが空

Flaskアプリが環境変数を読み取れていません。

```bash
# 手動で環境変数を設定してテスト
export BASE_PATH="/tournament"
cd /home/ike/tournament
source venv/bin/activate
python app.py
```

正常に動作する場合は、Supervisor設定の `environment` 行を確認してください。

## 技術詳細

### gunicorn_config.py

```python
import os

bind = "127.0.0.1:8001"
workers = 2
worker_class = "sync"
timeout = 120

# VPS環境用のBASE_PATH設定
# ローカル環境では空文字列として動作する
os.environ['BASE_PATH'] = '/tournament'
```

**注意**: 
- WSL(ローカル)環境でもVPS環境でも同じファイルを使用
- ローカルでは `app.config['BASE_PATH']` がこの値を上書き可能
- VPS環境ではSupervisorの `environment` 設定と組み合わせて使用

### app.py

```python
# 環境変数からBASE_PATHを読み取る（デフォルトは空文字列）
app.config['BASE_PATH'] = os.environ.get('BASE_PATH', '')

# すべてのテンプレートでbase_path変数を使用可能にする
@app.context_processor
def inject_base_path():
    return {'base_path': app.config['BASE_PATH']}
```

### テンプレート (add_tournament.html, edit_tournament.html)

```javascript
// base_path変数を使用してfetch URLを構築
const response = await fetch('{{ base_path }}/add', {
    method: 'POST',
    body: formData
});
```

- ローカル: `{{ base_path }}` = `""` → `/add`
- VPS: `{{ base_path }}` = `"/tournament"` → `/tournament/add`
