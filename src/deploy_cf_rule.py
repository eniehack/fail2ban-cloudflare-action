#!/usr/bin/env python3
"""
Cloudflare WAF Custom Rule Updater
既存ルールをJSONペイロードで更新
"""

import argparse
import json
import sys
import os
import requests
from typing import Dict, Any


def load_payload_from_file(filepath: str) -> Dict[str, Any]:
    """JSONファイルからペイロードを読み込み"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def load_payload_from_stdin() -> Dict[str, Any]:
    """標準入力からペイロードを読み込み"""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON from stdin: {e}", file=sys.stderr)
        sys.exit(1)


def update_rule(token: str, zone_id: str, ruleset_id: str, rule_id: str, payload: Dict[str, Any]) -> bool:
    """Custom Ruleを更新"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets/{ruleset_id}/rules/{rule_id}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print(f"Rule updated successfully: {rule_id}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error updating rule: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response:
            try:
                error_detail = e.response.json()
                print(f"API Error: {json.dumps(error_detail, indent=2)}", file=sys.stderr)
            except:
                print(f"Response: {e.response.text}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Update Cloudflare WAF Custom Rule with JSON payload",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cf_api.py --rule-file rule.json --ruleset-id abc123 --rule-id def456
  cat rule.json | python cf_api.py --stdin --ruleset-id abc123 --rule-id def456
  
Environment Variables:
  CF_API_TOKEN: Cloudflare API Token
  CF_ZONE_ID: Cloudflare Zone ID
  CF_RULESET_ID: Cloudflare Ruleset ID
  CF_RULE_ID: Cloudflare Rule ID
        """
    )
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--rule-file', help='JSON file containing rule payload')
    input_group.add_argument('--stdin', action='store_true', help='Read rule payload from stdin')
    
    args = parser.parse_args()
    
    # 環境変数から認証情報とIDを取得
    token = os.getenv('CF_API_TOKEN')
    zone_id = os.getenv('CF_ZONE_ID')
    ruleset_id = os.getenv('CF_RULESET_ID')
    rule_id = os.getenv('CF_RULE_ID')
    
    if not token:
        print("Error: CF_API_TOKEN required", file=sys.stderr)
        sys.exit(1)
    
    if not zone_id:
        print("Error: CF_ZONE_ID required", file=sys.stderr)
        sys.exit(1)
        
    if not ruleset_id:
        print("Error: CF_RULESET_ID required", file=sys.stderr)
        sys.exit(1)
        
    if not rule_id:
        print("Error: CF_RULE_ID required", file=sys.stderr)
        sys.exit(1)
    
    # ペイロード読み込み
    if args.rule_file:
        payload = load_payload_from_file(args.rule_file)
    else:
        payload = load_payload_from_stdin()
    
    # ルール更新
    success = update_rule(token, zone_id, ruleset_id, rule_id, payload)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
