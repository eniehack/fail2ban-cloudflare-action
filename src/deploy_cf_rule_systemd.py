#!/usr/bin/env python3
"""
Cloudflare WAF Rule Updater
IPリスト → ルール生成 → API更新を一括実行
既存のrule_generator.pyとcf_api.pyをインポートして使用
"""

import os
import sys
import json
from pathlib import Path
from cf_rulegen import (
    read_ips_from_file,
    generate_cloudflare_rule
)
from deploy_cf_rule import (
    update_rule
)

class CloudflareUpdater:
    def __init__(self, ip_file_path: str = "/var/log/fail2ban/blocked_ips.txt"):
        """初期化"""
        self.ip_file = Path(ip_file_path)
        
        # 環境変数から認証情報を取得
        self.token = os.getenv('CF_API_TOKEN')
        self.zone_id = os.getenv('CF_ZONE_ID')
        self.ruleset_id = os.getenv('CF_RULESET_ID')
        self.rule_id = os.getenv('CF_RULE_ID')
        
        # 必須環境変数のチェック
        missing = []
        if not self.token:
            missing.append('CF_API_TOKEN')
        if not self.zone_id:
            missing.append('CF_ZONE_ID')
        if not self.ruleset_id:
            missing.append('CF_RULESET_ID')
        if not self.rule_id:
            missing.append('CF_RULE_ID')
            
        if missing:
            print(f"Error: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
    
    def update_cloudflare_rules(self) -> bool:
        """IPリストを読み込み、ルール生成、API更新を実行"""
        print(f"Reading IP list from: {self.ip_file}")
        
        # 1. IPリストを読み込み (rule_generator.pyの関数を使用)
        ips = read_ips_from_file(self.ip_file)
        
        if not ips:
            print("No IPs to process, skipping update")
            return True
        
        print(f"Found {len(ips)} unique IP addresses")
        
        # 2. Cloudflare ルールを生成 (rule_generator.pyの関数を使用)
        rule_data = generate_cloudflare_rule(ips)

        if not rule_data:
            print("Failed to generate rule data")
            return False
        
        print("Generated Cloudflare rule:", file=sys.stderr)
        print(json.dumps(rule_data, indent=2), file=sys.stderr)
        
        # 3. Cloudflare API で更新 (cf_api.pyの関数を使用)
        success = update_rule(
            self.token,
            self.zone_id, 
            self.ruleset_id,
            self.rule_id,
            rule_data
        )
        
        if success:
            print("Cloudflare rule updated successfully", file=sys.stderr)
        else:
            print("Failed to update Cloudflare rule", file=sys.stderr)
        
        return success


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update Cloudflare WAF rules from fail2ban IP list",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables (required):
  CF_API_TOKEN: Cloudflare API Token
  CF_ZONE_ID: Cloudflare Zone ID  
  CF_RULESET_ID: Cloudflare Ruleset ID
  CF_RULE_ID: Cloudflare Rule ID

Example:
  python cloudflare_updater.py
  python cloudflare_updater.py --ip-file /custom/blocked_ips.txt
        """
    )
    
    parser.add_argument(
        '--ip-file', 
        default='/var/log/fail2ban/blocked_ips.txt',
        help='IP file path (default: /var/log/fail2ban/blocked_ips.txt)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true', 
        help='Generate rule but do not update API'
    )
    
    args = parser.parse_args()
    
    try:
        updater = CloudflareUpdater(args.ip_file)
        
        if args.dry_run:
            print("DRY RUN MODE - API will not be called")
            # IPリスト読み込みとルール生成のみ
            ips = read_ips_from_file(args.ip_file)
            if ips:
                rule_data = generate_cloudflare_rule(ips)
                if rule_data:
                    print("Generated rule:", file=sys.stderr)
                    print(json.dumps(rule_data, indent=2), file=sys.stderr)
            sys.exit(0)
        
        success = updater.update_cloudflare_rules()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
