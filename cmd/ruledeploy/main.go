package main

import (
	"context"
	"errors"
	"fmt"
	"io"
	"log"
	"os"

	"github.com/cloudflare/cloudflare-go/v5"
	"github.com/cloudflare/cloudflare-go/v5/option"
	"github.com/cloudflare/cloudflare-go/v5/rulesets"
	"github.com/urfave/cli/v3"
)

func ReadRuleFromReader(r io.Reader) (string, error) {
	data, err := io.ReadAll(r)
	if err != nil {
		return "", err
	}
	return string(data), nil
}

func ReadRuleFromFile(path string) (string, error) {
	f, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer f.Close()
	return ReadRuleFromReader(f)
}

func main() {
	cmd := &cli.Command{
		Name:  "ruledeploy",
		Usage: "deplot cloudflare custom rule from file or stdin.",
		Flags: []cli.Flag{
			&cli.BoolFlag{
				Name:  "stdin",
				Value: false,
			},
			&cli.StringFlag{
				Name:     "cf-api-token",
				Sources:  cli.EnvVars("CF_API_TOKEN"),
				Required: true,
			},
			&cli.StringFlag{
				Name:     "cf-zone-id",
				Sources:  cli.EnvVars("CF_ZONE_ID"),
				Required: true,
			},
			&cli.StringFlag{
				Name:     "cf-ruleset-id",
				Sources:  cli.EnvVars("CF_RULESET_ID"),
				Required: true,
			},
			&cli.StringFlag{
				Name:     "cf-rule-id",
				Sources:  cli.EnvVars("CF_RULE_ID"),
				Required: true,
			},
		},
		Arguments: []cli.Argument{
			&cli.StringArg{
				Name: "file",
			},
		},
		Action: func(ctx context.Context, c *cli.Command) error {
			filePath := c.StringArg("file")
			if !c.Bool("stdin") && len(filePath) == 0 {
				return errors.New("must be stdin option to true, or specify file path")
			}
			var rule string
			if c.Bool("stdin") {
				var err error
				rule, err = ReadRuleFromReader(os.Stdin)
				if err != nil {
					return err
				}
			} else {
				var err error
				rule, err = ReadRuleFromFile(filePath)
				if err != nil {
					return err
				}
			}
			client := cloudflare.NewClient(
				option.WithAPIToken(c.String("cf-api-token")),
			)
			params := rulesets.RuleEditParams{
				ZoneID: cloudflare.F(c.String("cf-zone-id")),
				Body: rulesets.RuleEditParamsBodyBlockRule{
					BlockRuleParam: rulesets.BlockRuleParam{
						Action:      cloudflare.F(rulesets.BlockRuleActionBlock),
						Description: cloudflare.F("fail2ban"),
						Enabled:     cloudflare.F(true),
						Expression:  cloudflare.F(rule),
					},
				},
			}
			resp, err := client.Rulesets.Rules.Edit(
				context.Background(),
				c.String("cf-ruleset-id"),
				c.String("cf-rule-id"),
				params,
			)
			if err != nil {
				return err
			}
			fmt.Println(resp.JSON)
			return nil
		},
	}

	if err := cmd.Run(context.Background(), os.Args); err != nil {
		log.Fatal(err)
	}
}
