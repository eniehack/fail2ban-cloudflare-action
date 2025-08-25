#!/usr/bin/env python3
"""
IP管理スクリプト
fail2banからのIP追加・削除を処理
"""

import sys
import os
import fcntl
import tempfile
import shutil
import argparse
from pathlib import Path


def add_ip(ip_file: Path, ip: str) -> None:
    """IPアドレスをファイルに追加"""
    # ファイルが存在しない場合は作成
    ip_file.parent.mkdir(parents=True, exist_ok=True)
    ip_file.touch(exist_ok=True)
    
    # まず既存IPを読み込み（重複チェック用）
    existing_ips = set()
    if ip_file.stat().st_size > 0:  # ファイルが空でない場合
        with ip_file.open('r') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # 共有ロック
            existing_ips = {line.strip() for line in f if line.strip()}
    
    # 重複チェック
    if ip in existing_ips:
        print(f"IP already exists: {ip}", file=sys.stderr)
        return
    
    # 追記
    with ip_file.open('a') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # 排他ロック
        f.write(f"{ip}\n")
        print(f"Added IP: {ip}", file=sys.stderr)


def remove_ip(ip_file: Path, ip: str) -> None:
    """IPアドレスをファイルから削除"""
    if not ip_file.exists():
        print(f"IP file not found: {ip_file}", file=sys.stderr)
        return
    
    # 一時ファイルを使用してアトミックに更新
    with ip_file.open('r') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        lines = f.readlines()
    
    # 指定されたIPを除外
    updated_lines = []
    found = False
    for line in lines:
        line_ip = line.strip()
        if line_ip and line_ip != ip:
            updated_lines.append(line)
        elif line_ip == ip:
            found = True
    
    # ファイルを更新
    with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=ip_file.parent) as temp_file:
        temp_file.writelines(updated_lines)
        temp_file.flush()
        os.fsync(temp_file.fileno())
    
    # アトミックに置換
    shutil.move(temp_file.name, ip_file)
    
    if found:
        print(f"Removed IP: {ip}", file=sys.stderr)
    else:
        print(f"IP not found: {ip}", file=sys.stderr)


def list_ips(ip_file: Path) -> None:
    """IPアドレスの一覧表示"""
    if not ip_file.exists():
        print("No IPs found (file does not exist)", file=sys.stderr)
        return
    
    with ip_file.open('r') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        lines = f.readlines()
    
    ips = [line.strip() for line in lines if line.strip()]
    
    if ips:
        print(f"Blocked IPs ({len(ips)}):", end='', file=sys.stderr)
        for ip in ips:
            print(f"  {ip}", end='', file=sys.stderr)
    else:
        print("No IPs found", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Manage blocked IP addresses")
    parser.add_argument('action', choices=['add', 'remove', 'list'], 
                       help='Action to perform')
    parser.add_argument('ip', nargs='?', help='IP address (required for add/remove)')
    parser.add_argument('--file', type=Path, default=Path('/var/log/fail2ban/blocked_ips.txt'),
                       help='IP file path (default: /var/log/fail2ban/blocked_ips.txt)')
    
    args = parser.parse_args()
    
    if args.action in ['add', 'remove'] and not args.ip:
        print(f"Error: IP address required for {args.action} action", file=sys.stderr)
        sys.exit(1)
    
    if args.action == 'add':
        add_ip(args.file, args.ip)
    elif args.action == 'remove':
        remove_ip(args.file, args.ip)
    elif args.action == 'list':
        list_ips(args.file)
    


if __name__ == "__main__":
    main()
