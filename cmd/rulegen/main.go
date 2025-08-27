package main

import (
	"bufio"
	"context"
	"errors"
	"fmt"
	"log"
	"net"
	"os"

	"github.com/eniehack/fail2ban-cloudflare-action/internal/rule"
	"github.com/urfave/cli/v3"
)

func ReadIPsFromStdin() ([]net.IP, error) {
	var ips []net.IP
	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		line := scanner.Text()
		ip := net.ParseIP(line)
		if ip != nil {
			ips = append(ips, ip)
		}
	}

	if err := scanner.Err(); err != nil {
		return nil, err
	}

	return ips, nil
}

func ReadIPsFromFile(path string) ([]net.IP, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var ips []net.IP
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		ip := net.ParseIP(line)
		if ip != nil {
			ips = append(ips, ip)
		}
	}

	if err := scanner.Err(); err != nil {
		return nil, err
	}

	return ips, nil
}

func main() {
	cmd := &cli.Command{
		Name:  "rulegen",
		Usage: "generate cloudflare custom rule from simple ip address list.",
		Flags: []cli.Flag{
			&cli.BoolFlag{
				Name:  "stdin",
				Value: false,
			},
		},
		Action: func(ctx context.Context, c *cli.Command) error {
			filePath := ""
			if 0 < c.Args().Len() {
				filePath = c.Args().Get(0)
			}
			if !c.Bool("stdin") && len(filePath) == 0 {
				return errors.New("must be stdin option to true, or specify file path")
			}
			var ips []net.IP
			if c.Bool("stdin") {
				var err error
				ips, err = ReadIPsFromStdin()
				if err != nil {
					return err
				}
			} else {
				var err error
				ips, err = ReadIPsFromFile(filePath)
				if err != nil {
					return err
				}
			}
			ruleStr := rule.GenerateRule(ips)
			fmt.Fprintln(os.Stdout, ruleStr)
			return nil
		},
	}
	if err := cmd.Run(context.Background(), os.Args); err != nil {
		log.Fatal(err)
	}
}
