# VPS環境バックアップガイド

## 概要

VPS環境の `/home/ike` ディレクトリを毎日自動バックアップする設定です。

## バックアップスクリプト

### 場所
```
/home/ike/backup_vps.sh
```

### 設定内容

- **バックアップ対象**: `/home/ike`
- **バックアップ先**: `/home/ike/backups/`
- **ファイル名形式**: `ike_backup_YYYYMMDD_HHMMSS.tar.gz`
- **保持期間**: 30日（それ以前は自動削除）
- **実行スケジュール**: 毎日深夜2時（cron）

### 除外ディレクトリ

以下のディレクトリはバックアップから除外されます：

- `/home/ike/backups/` - バックアップディレクトリ自体
- `.cache` - キャッシュファイル
- `*/venv` - Python仮想環境
- `*/__pycache__` - Pythonキャッシュ
- `*/node_modules` - Node.jsパッケージ
- `*/.git/objects` - Gitオブジェクト（容量削減）

## セットアップ手順

### 1. バックアップスクリプトの作成

```bash
nano /home/ike/backup_vps.sh
```

スクリプト内容を貼り付けて保存。

### 2. 実行権限の付与

```bash
chmod +x /home/ike/backup_vps.sh
```

### 3. 手動テスト実行

```bash
/home/ike/backup_vps.sh
```

成功すると以下のように表示されます：

```
Starting backup: /home/ike -> /home/ike/backups/ike_backup_20251205_233116.tar.gz
Backup completed successfully: ike_backup_20251205_233116.tar.gz
Backup size: 3.5G
Cleaning up old backups (older than 30 days)...
Current backup count: 1
```

### 4. cron設定（自動実行）

```bash
crontab -e
```

以下の行を追加：

```
0 2 * * * /home/ike/backup_vps.sh >> /home/ike/backup.log 2>&1
```

保存して終了。

### 5. cron設定の確認

```bash
crontab -l
```

## バックアップの確認

### バックアップファイル一覧

```bash
ls -lh /home/ike/backups/
```

### バックアップログ確認

```bash
cat /home/ike/backup.log
```

または最新10行のみ：

```bash
tail -n 10 /home/ike/backup.log
```

### ディスク使用量確認

```bash
du -sh /home/ike/backups/
```

## リストア（復元）手順

### 1. バックアップファイルの確認

```bash
ls -lh /home/ike/backups/
```

### 2. 復元するファイルを選択

```bash
# 例: 特定の日付のバックアップを復元
BACKUP_FILE="ike_backup_20251205_233116.tar.gz"
```

### 3. 復元先ディレクトリの作成

```bash
mkdir -p /tmp/restore
```

### 4. バックアップの展開

```bash
# 一時ディレクトリに展開
tar -xzf /home/ike/backups/${BACKUP_FILE} -C /tmp/restore

# 内容確認
ls -la /tmp/restore/ike/
```

### 5. 必要なファイルをコピー

```bash
# 例: tournamentディレクトリを復元
cp -r /tmp/restore/ike/tournament /home/ike/tournament_restored

# または特定のファイルのみ
cp /tmp/restore/ike/tournament/data/tournaments.json /home/ike/tournament/data/
```

### 6. クリーンアップ

```bash
rm -rf /tmp/restore
```

## トラブルシューティング

### バックアップが失敗する

**ログを確認**:
```bash
cat /home/ike/backup.log
```

**手動実行でエラー詳細を確認**:
```bash
/home/ike/backup_vps.sh
```

### ディスク容量不足

**現在のディスク使用量確認**:
```bash
df -h
```

**バックアップディレクトリのサイズ確認**:
```bash
du -sh /home/ike/backups/
```

**古いバックアップを手動削除**:
```bash
# 例: 7日以上前のバックアップを削除
find /home/ike/backups/ -name "ike_backup_*.tar.gz" -type f -mtime +7 -delete
```

### cronが実行されない

**cronサービスの確認**:
```bash
sudo systemctl status cron
```

**cronログの確認**:
```bash
sudo grep CRON /var/log/syslog
```

**環境変数の問題**:
cronはシェルの環境変数を引き継がないため、スクリプト内で絶対パスを使用しています。

## 保持期間の変更

`/home/ike/backup_vps.sh` の `RETENTION_DAYS` を編集：

```bash
nano /home/ike/backup_vps.sh
```

```bash
# 保持期間（日数）
RETENTION_DAYS=30  # この数値を変更
```

例：
- 7日間保持: `RETENTION_DAYS=7`
- 60日間保持: `RETENTION_DAYS=60`
- 90日間保持: `RETENTION_DAYS=90`

## バックアップスケジュールの変更

```bash
crontab -e
```

cron形式: `分 時 日 月 曜日 コマンド`

例：
```bash
# 毎日深夜2時（現在の設定）
0 2 * * * /home/ike/backup_vps.sh >> /home/ike/backup.log 2>&1

# 毎日午前3時
0 3 * * * /home/ike/backup_vps.sh >> /home/ike/backup.log 2>&1

# 毎週日曜日の午前2時
0 2 * * 0 /home/ike/backup_vps.sh >> /home/ike/backup.log 2>&1

# 毎月1日の午前2時
0 2 1 * * /home/ike/backup_vps.sh >> /home/ike/backup.log 2>&1

# 6時間ごと
0 */6 * * * /home/ike/backup_vps.sh >> /home/ike/backup.log 2>&1
```

## 注意事項

1. **ディスク容量の監視**: バックアップファイルは大きいため、定期的にディスク容量を確認してください
2. **オフサイトバックアップ**: VPS自体に障害が発生した場合に備え、定期的にローカルやクラウドストレージにもコピーすることを推奨
3. **復元テスト**: 定期的にバックアップからの復元テストを実行してください
4. **権限の確認**: バックアップスクリプトは通常ユーザー権限で実行されます

## セキュリティ

- バックアップファイルには機密情報が含まれる可能性があるため、適切なアクセス権限を設定してください
- バックアップディレクトリのパーミッション確認:
  ```bash
  ls -ld /home/ike/backups/
  ```

## 関連ドキュメント

- [WSLバックアップガイド](BACKUP.md) - WSL環境のバックアップ設定
- [デプロイガイド](DEPLOYMENT.md) - VPS環境のセットアップ手順
- [環境設定ガイド](ENVIRONMENT_SETUP.md) - 環境別の設定方法
