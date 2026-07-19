# RunCat Neo — Claude Code カスタムメトリクス

[RunCat Neo](https://github.com/runcat-dev/RunCatNeo) のカスタムメトリクス機能を使い、Claude Code の利用状況をメニューバー付近のダッシュボードに表示するためのスクリプトです。

参考: [RunCat Neo カスタムメトリクス入門](https://zenn.dev/kyome/articles/eb4a9f664002ad)

## 仕組み

Claude Code はセッション中、statusLine 用コマンドに JSON を stdin で渡します。`update-claude-metrics.py` がそれを RunCat 用 JSON に変換し、`~/.runcat/claude.json` に書き出します。RunCat Neo はそのファイルの変更を監視してダッシュボードを更新します。

```
Claude Code (statusLine)
  └─ stdin JSON → update-claude-metrics.py → ~/.runcat/claude.json → RunCat Neo
```

Claude Code を起動していない間は `claude.json` は更新されません。

## ファイル

| ファイル | 説明 |
|---------|------|
| `update-claude-metrics.py` | statusLine コマンド兼 RunCat 用 JSON 生成スクリプト |
| `~/.runcat/claude.json` | RunCat Neo が監視する出力ファイル（git 管理外・実行時に生成） |

## 表示項目

| 項目 | データ源 |
|------|---------|
| モデル | statusLine JSON の `model.display_name` |
| コンテキスト | `context_window.used_percentage` |
| 5時間 | `rate_limits.five_hour`（使用率・リセット時刻） |
| 7日 | `rate_limits.seven_day`（使用率・リセット時刻） |
| アクティブ | `~/.claude/sessions/` の PID 生存数 |

`rate_limits` は Claude.ai Pro/Max 向けで、セッション開始直後は `—` になることがあります（最初の API 応答後に値が入ります）。

## セットアップ

### 1. シンボリックリンクを作成

リポジトリルートで `link.sh` を実行します。

```bash
cd ~/dotfiles
./link.sh
```

`~/.runcat/update-claude-metrics.py` が dotfiles 内のスクリプトへのシンボリックリンクになります。

### 2. statusLine を登録

`.claude/settings.json` に statusLine が設定されています。別マシンで使う場合は `command` のパスを自分のホームディレクトリに合わせてください。

```json
{
  "statusLine": {
    "type": "command",
    "command": "/Users/yuta/.runcat/update-claude-metrics.py"
  }
}
```

`link.sh` 実行後、settings.json も `~/.claude/settings.json` にリンクされます。

### 3. RunCat Neo に登録

1. RunCat Neo を開く
2. **設定 → メトリクス → カスタムメトリクス**
3. **カスタムメトリクスのソースを追加** で `~/.runcat/claude.json` を選択

隠しファイルは `Command + Shift + .` で表示するか、`Command + Shift + G` でパスを直接入力してください。

### 4. メニューバー表示（任意）

メトリクスバーを有効にし、Claude Code メトリクスのトグルをオンにすると、`metricsBarValue`（5時間使用率、なければコンテキスト %）がメニューバーに表示されます。

## 動作確認

Claude Code セッション中にファイルの更新時刻が動くことを確認します。

```bash
ls -la ~/.runcat/claude.json
```

手動でスクリプトだけ試す場合:

```bash
printf '{}' | python3 ~/.runcat/update-claude-metrics.py
python3 -m json.tool ~/.runcat/claude.json
```

## 環境変数

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `RUNCAT_OUT_FILE` | `~/.runcat/claude.json` | 出力先 JSON のパス |

## 前提条件

- Python 3（標準ライブラリのみ・pip 不要）
- [RunCat Neo](https://github.com/runcat-dev/RunCatNeo)
- [Claude Code](https://code.claude.com/)（Pro/Max で 5h/7d 枠を表示する場合）

## トラブルシューティング

| 症状 | 確認・対処 |
|------|-----------|
| RunCat に何も表示されない | `claude.json` が存在するか。RunCat にソース登録済みか |
| 値が更新されない | Claude Code セッション中か。`claude.json` の mtime が動くか |
| 5h/7d が `—` のまま | Pro/Max プランか。最初の応答後に再描画されるか待つ |
| statusLine が動かない | `settings.json` の `command` パスが正しいか。スクリプトに実行権限があるか |
