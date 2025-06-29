#!/bin/bash

files_and_paths=(
  "./.claude/CLAUDE.md:~/.claude"
)

create_symlink() {
  local source_file=$(realpath $1)
  local destination_path=$2
  echo "Creating symlink from $source_file to $destination_path"
  
  backup_file="${destination_path}.bak"

  if [ -e "$destination_path" ]; then
    mv "$destination_path" "$backup_file"
  fi

  ln -s "$source_file" "$destination_path"
}

for entry in "${files_and_paths[@]}"; do
  IFS=":" read -r source_file destination_path <<< "$entry"
  create_symlink "$source_file" "$destination_path"
done