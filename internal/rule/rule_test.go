package rule

import (
	"net"
	"testing"
)

func TestGenerateRule(t *testing.T) {
	tests := []struct {
		Name  string
		Input []net.IP
		Want  string
	}{
		{
			Name: "length 1",
			Input: []net.IP{
				net.ParseIP("192.168.1.1"),
			},
			Want: "(ip.src eq 192.168.1.1)",
		},
		{
			Name: "simple",
			Input: []net.IP{
				net.ParseIP("192.168.1.1"),
				net.ParseIP("192.168.1.2"),
			},
			Want: "(ip.src eq 192.168.1.1 or ip.src eq 192.168.1.2)",
		},
	}

	for _, tt := range tests {
		t.Run(tt.Name, func(t *testing.T) {
			if got := GenerateRule(tt.Input); got != tt.Want {
				t.Errorf("GenerateRule() = '%s', want '%s'\n", got, tt.Want)
			}
		})
	}
}
