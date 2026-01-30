#!/bin/bash

files_and_paths=(
  "./.claude/CLAUDE.md:~/.claude/CLAUDE.md"
  "./.claude/settings.json:~/.claude/settings.json"
  "./.raycast-scripts/:~/.raycast-scripts/"
)

create_symlink() {
  local source_path=$1
  local destination_path=$2

  # ~ をホームディレクトリに展開
  destination_path="${destination_path/#\~/$HOME}"
  
  # source_path の絶対パスを取得（存在しない場合はそのまま使うが、通常は存在するはず）
  if [ -e "$source_path" ]; then
    local real_source_path=$(realpath "$source_path")
  else
    echo "Warning: Source $source_path does not exist. Skipping."
    return
  fi

  if [ -d "$real_source_path" ]; then
    # --- ソースがディレクトリの場合 ---
    echo "Processing directory: $real_source_path"
    
    # リンク先ディレクトリが存在しない場合は作成
    if [ ! -d "$destination_path" ]; then
        echo "Creating directory: $destination_path"
        mkdir -p "$destination_path"
    fi

    # 隠しファイルも含める設定
    shopt -s dotglob nullglob

    # ディレクトリ内の各ファイルについて再帰的に処理
    for file in "$real_source_path"/*; do
        local filename=$(basename "$file")
        # 再帰呼び出し
        create_symlink "$file" "$destination_path/$filename"
    done
    
    # 設定を戻す
    shopt -u dotglob nullglob

  else
    # --- ソースがファイルの場合 ---
    
    # 親ディレクトリが存在することを確認して作成
    local dest_dir=$(dirname "$destination_path")
    if [ ! -d "$dest_dir" ]; then
        echo "Creating parent directory: $dest_dir"
        mkdir -p "$dest_dir"
    fi

    # 既に正しいリンクが貼られている場合はスキップ
    if [ -L "$destination_path" ] && [ "$(readlink "$destination_path")" == "$real_source_path" ]; then
        # echo "Link already exists: $destination_path"
        return
    fi

    echo "Creating symlink from $real_source_path to $destination_path"
    
    # 既存ファイルのバックアップ処理（リンクではなく実ファイルが存在する場合や、異なるリンクの場合）
    if [ -e "$destination_path" ] || [ -L "$destination_path" ]; then
      local backup_file="${destination_path}.bak"
      echo "Backing up existing file to $backup_file"
      mv "$destination_path" "$backup_file"
    fi

    ln -s "$real_source_path" "$destination_path"
  fi
}

for entry in "${files_and_paths[@]}"; do
  IFS=":" read -r source_file destination_path <<< "$entry"
  create_symlink "$source_file" "$destination_path"
done
