# Raycast Scripts

このディレクトリは、[Raycast](https://www.raycast.com/) の [Script Commands](https://github.com/raycast/script-commands) として実行されるスクリプトを管理するためのものです。

## 収録スクリプト

### Audio Switching
Macのオーディオ出力デバイスを素早く切り替えるためのスクリプトです。以下のスクリプトは `switchaudio-osx` コマンドを利用しています。

- **switchaudiosource-oundcoreLiberty4.sh**: オーディオ出力を `soundcore Liberty 4` に切り替えます。
- **switchaudiosource-Scarlett2i2USB.sh**: オーディオ出力を `Scarlett 2i2 USB` に切り替えます。

## 前提条件

音声切り替えスクリプトを使用するには、`switchaudio-osx` がインストールされている必要があります。まだの場合は、Homebrewを使用してインストールしてください。

```bash
# インストール
brew install switchaudio-osx

# 出力デバイス一覧
SwitchAudioSource -f json -t output -a | jq

```

## 設定方法

1. Raycastの設定画面 (`cmd` + `,`) を開きます。
2. **Extensions** タブを選択し、サイドバーから **Script Commands** を選択します。
3. **Add Directories** をクリックし、この `.raycast-scripts` ディレクトリを追加します。
4. 追加されると、Raycastから各スクリプト名（例: "SwitchAudioSource-soundcore-Liberty-4"）で検索・実行できるようになります。
