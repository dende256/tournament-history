# トーナメント大会履歴管理システム

トーナメント大会の記録を管理・閲覧できるWebアプリケーションです。

## 機能

- ✅ 大会情報の登録・編集・削除
- ✅ 大会名、日程、主催者の管理
- ✅ 1-3位の入賞者記録
- ✅ トーナメント表画像のアップロード
- ✅ 大会詳細説明の記録
- ✅ 大会一覧表示（日付順）
- ✅ レスポンシブデザイン

## セットアップ

### 1. 仮想環境の作成
```bash
cd /home/ike/tournament
python3 -m venv venv
source venv/bin/activate
```

### 2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 3. 開発サーバーの起動
```bash
python app.py
```

ブラウザで `http://localhost:5001` にアクセス

## 本番環境デプロイ

### Gunicornでの起動
```bash
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### Nginx設定例
```nginx
server {
    listen 80;
    server_name tournament.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads {
        alias /home/ike/tournament/uploads;
    }

    client_max_body_size 16M;
}
```

### Supervisor設定例
```ini
[program:tournament-app]
directory=/home/ike/tournament
command=/home/ike/tournament/venv/bin/gunicorn -w 4 -b 127.0.0.1:5001 app:app
user=ike
autostart=true
autorestart=true
stderr_logfile=/var/log/tournament-app.err.log
stdout_logfile=/var/log/tournament-app.out.log
```

## データ保存

- 大会データ: `data/tournaments.json`
- アップロード画像: `uploads/`

## 必要項目

- 大会名（必須）
- 開催日（必須）
- 主催者（必須）
- 1位入賞者（必須）
- 2位入賞者（任意）
- 3位入賞者（任意）
- トーナメント表画像（任意）
- 大会詳細（任意）
