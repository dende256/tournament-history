# Tournament History Management System

トーナメント大会の履歴を管理するWebアプリケーション

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1.0-green.svg)

## 概要

トーナメント大会の記録を簡単に管理・共有できるWebアプリケーションです。大会情報、入賞者、トーナメント表の画像を登録・閲覧できます。

**デモサイト**: https://example.com/tournament/

## 主な機能

- 🏆 大会情報の登録（大会名、開催日、主催者、1-3位入賞者）
- 📊 トーナメント表の画像アップロード（PNG/JPG/GIF/WEBP対応）
- 📋 大会一覧の表示（日付順ソート）
- 👁️ 大会詳細の閲覧（表彰台表示、画像ビューア）
- ✏️ 大会情報の編集・削除
- 🎨 レスポンシブデザイン（水色グラデーション）
- 💾 JSON形式でのデータ永続化

## 技術スタック

- **Backend**: Flask 3.1.0
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Data Storage**: JSON
- **File Upload**: Werkzeug
- **Production Server**: Gunicorn + Nginx + Supervisor
- **SSL**: Let's Encrypt

## ディレクトリ構造

```
tournament/
├── app.py                    # メインアプリケーション
├── requirements.txt          # Python依存パッケージ
├── gunicorn_config.py       # Gunicorn設定
├── README.md                # このファイル
├── DEPLOYMENT.md            # デプロイ手順書
├── templates/               # HTMLテンプレート
│   ├── base.html           # ベーステンプレート
│   ├── index.html          # 大会一覧
│   ├── tournament_detail.html  # 大会詳細
│   ├── add_tournament.html     # 大会登録
│   └── edit_tournament.html    # 大会編集
├── data/                    # データ保存ディレクトリ
│   └── tournaments.json    # 大会データ（自動生成）
└── uploads/                 # 画像アップロードディレクトリ
```

## 開発環境セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/YOUR_USERNAME/tournament-history.git
cd tournament-history
```

### 2. 仮想環境の作成と有効化

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows
```

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. アプリケーションの起動

```bash
python app.py
```

ブラウザで http://localhost:5001 にアクセスしてください。

## 本番環境へのデプロイ

詳細な手順は [DEPLOYMENT.md](DEPLOYMENT.md) を参照してください。

### クイックスタート

```bash
# Gunicornで起動
gunicorn -c gunicorn_config.py app:app
```

### Nginx + Supervisor構成

完全な本番環境構成（Nginx リバースプロキシ、Supervisor プロセス管理、SSL対応）の手順は [DEPLOYMENT.md](DEPLOYMENT.md) を参照してください。

## API エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/` | 大会一覧表示 |
| GET | `/tournament/<id>` | 大会詳細表示 |
| GET | `/add` | 大会登録フォーム |
| POST | `/add` | 大会登録処理 |
| GET | `/edit/<id>` | 大会編集フォーム |
| POST | `/edit/<id>` | 大会更新処理 |
| POST | `/delete/<id>` | 大会削除処理 |

## データ構造

大会データは以下のJSON形式で保存されます：

```json
{
  "id": "uuid-string",
  "tournament_name": "第1回 春季トーナメント",
  "date": "2025-12-04",
  "organizer": "○○協会",
  "first_place": "優勝者名",
  "second_place": "準優勝者名",
  "third_place": "3位入賞者名",
  "description": "大会の詳細説明",
  "bracket_image": "画像ファイル名.png",
  "created_at": "2025-12-04T12:00:00",
  "updated_at": "2025-12-04T13:00:00"
}
```

## セキュリティ

- ファイルアップロード: `werkzeug.secure_filename` を使用
- 許可拡張子: PNG, JPG, JPEG, GIF, WEBP
- 最大ファイルサイズ: 16MB
- XSS対策: Jinja2テンプレートエンジンの自動エスケープ

## ライセンス

MIT License

## 作者

- GitHub: https://github.com/dende256

## 関連プロジェクト

- [Bradley-Terry Rating System](https://github.com/YOUR_USERNAME/rating-system) - 1対1対戦のレーティング算出システム
