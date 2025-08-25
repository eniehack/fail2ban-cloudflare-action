#!/usr/bin/env python3
"""
Cloudflare Custom Rule Generator
IPアドレスリストからCloudflare WAF Custom Ruleを生成
"""

import argparse
import json
import sys
import ipaddress
from pathlib import Path
from typing import List, Dict, Any


def validate_ip(ip_str: str) -> bool:
    """IPアドレスの形式を検証"""
    try:
        ipaddress.ip_address(ip_str.strip())
        return True
    except ValueError:
        return False


def read_ips_from_file(filepath: Path) -> List[str]:
    """ファイルからIPアドレスを読み込み"""
    try:
        with open(filepath, 'r') as f:
            ips = []
            for line_num, line in enumerate(f, 1):
                ip = line.strip()
                if not ip or ip.startswith('#'):  # 空行とコメント行をスキップ
                    continue
                if validate_ip(ip):
                    ips.append(ip)
                else:
                    print(f"Warning: Invalid IP at line {line_num}: {ip}", file=sys.stderr)
            return list(set(ips))  # 重複除去
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


def parse_ip_list(ip_string: str) -> List[str]:
    """カンマ区切りの文字列からIPアドレスを解析"""
    ips = []
    for ip in ip_string.split(','):
        ip = ip.strip()
        if validate_ip(ip):
            ips.append(ip)
        else:
            print(f"Warning: Invalid IP: {ip}", file=sys.stderr)
    return list(set(ips))  # 重複除去


def generate_cloudflare_rule(ips: List[str], rule_name: str = "fail2ban-blocked-ips") -> Dict[str, Any]:
    """Cloudflare Custom Ruleを生成"""
    if not ips:
        print("Error: No valid IPs provided", file=sys.stderr)
        sys.exit(1)
    
    # IP条件を構築（OR条件で複数IP）
    if len(ips) == 1:
        expression = f'(ip.src eq {ips[0]})'
    else:
        ip_conditions = [f'ip.src eq {ip}' for ip in ips]
        expression = f'({" or ".join(ip_conditions)})'
    
    rule = {
        "action": "block",
        "expression": expression,
        "description": "fail2ban",
        "enabled": True
    }
    
    return rule


def main():
    parser = argparse.ArgumentParser(
        description="Generate Cloudflare Custom Rule from IP list",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rule_generator.py -i blocked_ips.txt
  python rule_generator.py --ips "1.2.3.4,5.6.7.8"
  python rule_generator.py -i blocked_ips.txt -o rule.json
        """
    )
    
    parser.add_argument('-i', '--input', help='Input file containing IP addresses (one per line)', required=True)
    
    parser.add_argument('-o', '--output', help='Output JSON file (default: stdout)')
    parser.add_argument('--rule-name', default='fail2ban-blocked-ips', 
                       help='Rule name/description prefix (default: fail2ban-blocked-ips)')
    parser.add_argument('--format', choices=['json', 'compact'], default='json',
                       help='Output format (default: json)')
    
    args = parser.parse_args()
    
    ips = read_ips_from_file(args.input)
    
    if not ips:
        print("Error: No valid IP addresses found", file=sys.stderr)
        sys.exit(1)
    
    print(f"Processing {len(ips)} unique IP addresses", file=sys.stderr)
    
    # ルール生成
    rule = generate_cloudflare_rule(ips, args.rule_name)
    
    # 出力
    if args.format == 'compact':
        output = json.dumps(rule, separators=(',', ':'))
    else:
        output = json.dumps(rule, indent=2, ensure_ascii=False)
    
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Rule written to {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing to file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)


if __name__ == "__main__":
    main()
