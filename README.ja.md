# fail2ban-cloudflare-action

fail2banのactionとしてcloudflare custom ruleを操作するためのスクリプト群

- rulegen - 1行ごとにipアドレスが記述されたテキストファイルを受け取り、Cloudflare custom ruleを生成する
- ipmglist.py - ipアドレスをBAN/un-BANするためのスクリプト。jail.localから呼び出されることを想定
- ruledeploy - Cloudflare APIを使ってcustom ruleをdeployする

## install

### depends

- python3
- requests (pythonのライブラリ。deploy_cf_rule.py または deploy_cf_rule_systemd.pyを利用する際に必要)
- inotifywait (dnf、aptのリポジトリではinotify-toolsパッケージに同梱されています。`contrib/iplistwatch.sh`を利用する場合には必要)
