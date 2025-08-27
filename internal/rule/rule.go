package rule

import (
	"fmt"
	"net"
	"strings"
)

func GenerateRule(targetIp []net.IP) string {
	if len(targetIp) == 0 {
		return ""
	} else if len(targetIp) == 1 {
		return fmt.Sprintf("(ip.src eq %s)", targetIp[0].String())
	}
	singleRule := make([]string, 0, len(targetIp))
	for _, ip := range targetIp {
		singleRule = append(singleRule, fmt.Sprintf("ip.src eq %s", ip.String()))
	}
	rule := new(strings.Builder)
	fmt.Fprintf(rule, "(")
	fmt.Fprint(rule, strings.Join(singleRule, " or "))
	fmt.Fprintf(rule, ")")
	return rule.String()
}

type CloudflareAPICustomRuleRequestPayload struct {
	Action     string `json:"action"`
	Expression string `json:"expression"`
	Name       string `json:"Description"`
	Enabled    bool   `json:"enabled"`
}

func MakeRequestPayload(name string, expression string) *CloudflareAPICustomRuleRequestPayload {
	return &CloudflareAPICustomRuleRequestPayload{
		Action:     "block",
		Expression: expression,
		Name:       name,
		Enabled:    true,
	}
}
