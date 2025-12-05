# Tournament History Management System

トーナメント大会の履歴を管理するWebアプリケーション

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1.0-green.svg)

## 概要

トーナメント大会の記録を簡単に管理・共有できるWebアプリケーションです。大会情報、入賞者、トーナメント表の画像を登録・閲覧できます。

## 主な機能

- 🏆 大会情報の登録（大会名、開催日、主催者、1-3位入賞者）
- 📊 トーナメント表の画像アップロード（PNG/JPG/GIF/WEBP対応）
- 🎥 YouTube動画の埋め込み（watch、live、短縮URLに対応）
- 📋 大会一覧の表示（日付順ソート）
- 👁️ 大会詳細の閲覧（表彰台表示、画像ビューア、動画プレーヤー）
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
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "created_at": "2025-12-04T12:00:00",
  "updated_at": "2025-12-04T13:00:00"
}
```

### YouTube URL対応形式

以下のYouTube URL形式に対応しており、自動的に埋め込み形式に変換されます：

- 通常の動画: `https://www.youtube.com/watch?v=VIDEO_ID`
- ライブ配信: `https://www.youtube.com/live/VIDEO_ID`
- 短縮URL: `https://youtu.be/VIDEO_ID`
- 直接埋め込み: `https://www.youtube.com/embed/VIDEO_ID`

動画は16:9のレスポンシブなiframeで表示されます。

## セキュリティ

- ファイルアップロード: `werkzeug.secure_filename` を使用
- 許可拡張子: PNG, JPG, JPEG, GIF, WEBP
- 最大ファイルサイズ: 16MB
- XSS対策: Jinja2テンプレートエンジンの自動エスケープ

## 更新履歴

### v1.2.0 (2025-12-05)

**複数YouTube動画対応**

- **新機能**:
  - 1つの大会に最大5つのYouTube動画URLを登録可能に拡張
  - 詳細ページで複数の動画を縦に並べて表示

- **技術的変更**:
  - データモデル変更: `youtube_url` → `youtube_url_1` ~ `youtube_url_5`
  - `view_tournament()` で複数URLの変換処理に対応
  - `add_tournament.html` に5個のURL入力欄を追加
  - `edit_tournament.html` に5個のURL入力欄を追加（既存値表示対応）
  - `tournament_detail.html` でループ処理による複数動画表示

- **互換性**:
  - 既存データ（`youtube_url`のみ）との下位互換性を維持

### v1.1.0 (2025-12-05)

**YouTube動画埋め込み機能の追加**

- **新機能**:
  - 大会詳細ページへのYouTube動画埋め込み対応
  - YouTube URL入力フィールドを追加・編集フォームに追加
  - 複数のYouTube URL形式に対応（watch、live、短縮URL）
  - レスポンシブな16:9動画プレーヤーの実装

- **技術的変更**:
  - `convert_youtube_url()` 関数の追加（`app.py`）
    - YouTube URLを埋め込み形式に自動変換
    - 対応形式: `watch?v=`, `/live/`, `youtu.be/`, `/v/`, `/embed/`
  - `view_tournament()` でYouTube URL変換処理を追加
  - `tournament_detail.html` に動画セクション追加
  - `add_tournament.html` および `edit_tournament.html` にYouTube URL入力フィールド追加
  - データモデルに `youtube_url` フィールド追加

- **バグ修正**:
  - Flask routing修正: `/tournament/<id>` → `/<id>` (Nginx proxy_pass対応)
  - リダイレクトURL修正: `url_for()` → `f"/tournament/{id}"` (絶対パス指定)

- **インフラ変更**:
  - Nginx設定との整合性を確保
  - Supervisor経由でのGunicorn再起動手順を確立

### v1.0.0 (2025-12-04)

- 初回リリース
- 基本的な大会管理機能の実装

## ライセンス

MIT License

## 作者

- GitHub: https://github.com/dende256

## 関連プロジェクト

- [Bradley-Terry Rating System](https://github.com/YOUR_USERNAME/rating-system) - 1対1対戦のレーティング算出システム
