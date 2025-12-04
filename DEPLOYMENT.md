# デプロイ手順書

Tournament History Management System を本番環境（VPS）にデプロイする手順を説明します。

## 前提条件

- Debian/Ubuntu系Linux VPS
- Python 3.8以上
- root権限またはsudo権限
- ドメイン名（SSL証明書取得のため）

## 環境情報

本ドキュメントは以下の環境でテスト済みです：
- OS: Debian
- Python: 3.11
- サーバー: ConoHa VPS
- ドメイン: your-domain.example.com
- アプリURL: https://your-domain.example.com/tournament/

## デプロイ手順

### 1. VPSへの接続とディレクトリ準備

```bash
# VPSにSSH接続
ssh user@your-vps-ip

# アプリケーションディレクトリを作成
mkdir -p /home/xxx/tournament/templates
mkdir -p /home/xxx/tournament/data
mkdir -p /home/xxx/tournament/uploads
cd /home/xxx/tournament
```

### 2. ファイルの転送

ローカルマシンから以下のファイルをVPSに転送します：

#### 必須ファイル
- `app.py` - メインアプリケーション
- `requirements.txt` - 依存パッケージリスト
- `gunicorn_config.py` - Gunicorn設定
- `templates/` - 全HTMLテンプレート（5ファイル）
  - base.html
  - index.html
  - tournament_detail.html
  - add_tournament.html
  - edit_tournament.html

#### 転送方法の例

**方法1: SCP**
```bash
# ローカルマシンから実行
scp -r app.py requirements.txt gunicorn_config.py templates/ user@your-vps-ip:/home/xxx/tournament/
```

**方法2: Git**
```bash
# VPS上で実行
git clone https://github.com/YOUR_USERNAME/tournament-history.git /home/xxx/tournament
```

**方法3: 手動コピー**
nanoエディタで各ファイルを作成し、内容をコピー&ペースト

### 3. Python環境のセットアップ

```bash
cd /home/xxx/tournament

# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化
source venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 4. Gunicorn設定ファイルの作成

`gunicorn_config.py` を作成（既に転送済みの場合はスキップ）：

```python
bind = "127.0.0.1:8001"
workers = 2
worker_class = "sync"
timeout = 120
```

### 5. Supervisor設定

Supervisorでアプリケーションを管理します。

#### Supervisorのインストール（未インストールの場合）

```bash
sudo apt update
sudo apt install supervisor
```

#### Supervisor設定ファイルの作成

```bash
sudo nano /etc/supervisor/conf.d/tournament-app.conf
```

以下の内容を記述：

```ini
[program:tournament-app]
command=/home/xxx/tournament/venv/bin/gunicorn -c gunicorn_config.py app:app
directory=/home/xxx/tournament
user=xxx
autostart=true
autorestart=true
stderr_logfile=/var/log/tournament-app.err.log
stdout_logfile=/var/log/tournament-app.out.log
```

#### Supervisorに設定を読み込ませる

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start tournament-app

# ステータス確認
sudo supervisorctl status
```

### 6. Nginx設定

#### Nginxのインストール（未インストールの場合）

```bash
sudo apt install nginx
```

#### Nginx設定ファイルの編集

既存のNginx設定ファイルに追加します。

**HTTPSを使用している場合**（推奨）:

```bash
sudo nano /etc/nginx/sites-available/rating-app
```

または

```bash
sudo nano /etc/nginx/sites-available/default
```

`location /` ブロックの後に以下を追加：

```nginx
# Tournament app (port 8001)
location /tournament/ {
    proxy_pass http://127.0.0.1:8001/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
}
```

#### Nginx設定のテストとリロード

```bash
# 設定ファイルの文法チェック
sudo nginx -t

# Nginxをリロード
sudo systemctl reload nginx
```

### 7. SSL証明書の設定（Let's Encrypt）

既存のドメインにSSLが設定済みの場合は、自動的に適用されます。

新規にSSLを設定する場合：

```bash
# Certbotのインストール
sudo apt install certbot python3-certbot-nginx

# SSL証明書の取得
sudo certbot --nginx -d yourdomain.com

# 自動更新の確認
sudo systemctl status certbot.timer
```

### 8. 動作確認

#### ステータス確認

```bash
# Supervisorのステータス
sudo supervisorctl status

# Nginxのステータス
sudo systemctl status nginx

# ポート確認
sudo netstat -tlnp | grep 8001
```

#### ログ確認

```bash
# アプリケーションログ
sudo tail -50 /var/log/tournament-app.out.log
sudo tail -50 /var/log/tournament-app.err.log

# Nginxログ
sudo tail -50 /var/log/nginx/access.log
sudo tail -50 /var/log/nginx/error.log
```

#### 動作テスト

```bash
# ローカルでアプリケーションに直接アクセス
curl http://127.0.0.1:8001/

# 外部からアクセス
# ブラウザで https://yourdomain.com/tournament/ を開く
```

## ファイル構成（VPS上）

```
/home/xxx/tournament/
├── app.py
├── requirements.txt
├── gunicorn_config.py
├── venv/                    # 仮想環境
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── tournament_detail.html
│   ├── add_tournament.html
│   └── edit_tournament.html
├── data/
│   └── tournaments.json     # 自動生成
└── uploads/                 # 自動生成
```

## トラブルシューティング

### アプリケーションが起動しない

```bash
# ログを確認
sudo tail -100 /var/log/tournament-app.err.log

# 仮想環境を確認
cd /home/xxx/tournament
source venv/bin/activate
python app.py  # 手動で起動してエラーを確認
```

### 404 Not Found

**症状: 一覧ページは表示されるが、詳細ページで404エラー**

原因: Flask routingとNginx設定の不整合

解決方法:
1. `app.py` のルーティングを確認
```bash
grep "@app.route" app.py
# 出力: @app.route('/<tournament_id>')  ← これが正しい
```

2. Nginx設定を確認
```bash
sudo nginx -T | grep -A 10 "location /tournament"
# proxy_pass に trailing slash (/) があることを確認
```

3. Gunicornのキャッシュをクリア
```bash
sudo supervisorctl stop tournament-app
sudo supervisorctl start tournament-app
# restart ではなく stop → start を実行
```

**症状: 全てのページで404エラー**

1. Nginx設定を確認
```bash
sudo nginx -T | grep -A 10 "location /tournament"
```

2. HTTPSを使用している場合、HTTPS用のserverブロックに設定があるか確認

3. Nginxを再起動
```bash
sudo systemctl restart nginx
```

### YouTube動画が表示されない

1. URLフォーマットが正しいか確認
```bash
# 対応形式:
# https://www.youtube.com/watch?v=VIDEO_ID
# https://www.youtube.com/live/VIDEO_ID
# https://youtu.be/VIDEO_ID
```

2. データに保存されているか確認
```bash
cat data/tournaments.json | grep youtube_url
```

3. テンプレートが最新版か確認
```bash
grep "youtube_embed_url" templates/tournament_detail.html
```

### 画像がアップロードできない

1. uploadsディレクトリの権限を確認
```bash
ls -la /home/xxx/tournament/uploads/
sudo chown -R xxx:xxx /home/xxx/tournament/uploads/
sudo chmod 755 /home/xxx/tournament/uploads/
```

2. Nginx設定でclient_max_body_sizeを確認

### データが保存されない

1. dataディレクトリの権限を確認
```bash
ls -la /home/xxx/tournament/data/
sudo chown -R xxx:xxx /home/xxx/tournament/data/
sudo chmod 755 /home/xxx/tournament/data/
```

## メンテナンス

### アプリケーションの再起動

```bash
sudo supervisorctl restart tournament-app
```

### ログのローテーション

```bash
# ログファイルをアーカイブ
sudo logrotate -f /etc/logrotate.d/supervisor
```

### アップデート手順

```bash
cd /home/xxx/tournament
source venv/bin/activate

# コードを更新（Git使用の場合）
git pull origin main

# 依存パッケージを更新
pip install -r requirements.txt --upgrade

# アプリケーションを再起動
sudo supervisorctl stop tournament-app
sudo supervisorctl start tournament-app

# 注意: restart コマンドではなく stop → start を使用
# Gunicornのコードキャッシュをクリアするため
```

### 主要な更新内容

#### v1.1.0 (2025-12-05) - YouTube動画埋め込み機能

**追加されたファイル:**
- `templates/tournament_detail.html` の更新（YouTube埋め込みセクション）

**変更されたファイル:**
- `app.py`: `convert_youtube_url()` 関数の追加
- `templates/add_tournament.html`: YouTube URL入力フィールド追加
- `templates/edit_tournament.html`: YouTube URL入力フィールド追加

**Flask routing重要な変更:**
- `@app.route('/tournament/<id>')` → `@app.route('/<id>')`
- Nginxの `proxy_pass http://127.0.0.1:8001/;` (trailing slash) に対応
- リダイレクトURLを `url_for()` から絶対パス `f"/tournament/{id}"` に変更

**更新後の確認:**
```bash
# Flaskアプリが正常に動作しているか確認
curl -I http://127.0.0.1:8001/

# YouTube機能が動作するか確認（大会詳細ページ）
curl http://127.0.0.1:8001/<tournament-id> | grep youtube
```

## セキュリティ推奨事項

1. **ファイアウォールの設定**
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

2. **定期的なバックアップ**
```bash
# データのバックアップ
tar -czf tournament-backup-$(date +%Y%m%d).tar.gz /home/ike/tournament/data /home/ike/tournament/uploads
```

3. **SSL証明書の自動更新確認**
```bash
sudo certbot renew --dry-run
```

## パフォーマンスチューニング

### Gunicornワーカー数の調整

`gunicorn_config.py` で調整：

```python
# CPU数の2-4倍が推奨
workers = 4
```

### Nginx設定の最適化

```nginx
client_max_body_size 16M;
client_body_buffer_size 128k;
```

## 参考情報

- [Flask公式ドキュメント](https://flask.palletsprojects.com/)
- [Gunicorn公式ドキュメント](https://gunicorn.org/)
- [Nginx公式ドキュメント](https://nginx.org/en/docs/)
- [Supervisor公式ドキュメント](http://supervisord.org/)
- [Let's Encrypt公式サイト](https://letsencrypt.org/)
