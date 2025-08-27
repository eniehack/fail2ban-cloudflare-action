# fail2ban-cloudflare-action

fail2banのactionとしてcloudflare custom ruleを操作するためのスクリプト群

- cf_rulegen.py - 1行ごとにipアドレスが記述されたテキストファイルを受け取り、Cloudflare custom ruleを生成する
- ipmglist.py - ipアドレスをBAN/un-BANするためのスクリプト。jail.localから呼び出されることを想定
- deploy_cf_rule.py - Cloudflare APIを使ってcustom ruleをdeployする
- deploy_cf_rule_systemd.py - deploy_cf_rule.pyをsystemd-timerで呼び出すためのスクリプト。

## install

### depends

- python3
- requests (pythonのライブラリ。deploy_cf_rule.py または deploy_cf_rule_systemd.pyを利用する際に必要)
- inotifywait (dnf、aptのリポジトリではinotify-toolsパッケージに同梱されています。`contrib/iplistwatch.sh`を利用する場合には必要)
