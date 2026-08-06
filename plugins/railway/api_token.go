package railway

import (
	"context"

	"github.com/1Password/shell-plugins/sdk"
	"github.com/1Password/shell-plugins/sdk/importer"
	"github.com/1Password/shell-plugins/sdk/schema"
	"github.com/1Password/shell-plugins/sdk/schema/credname"
	"github.com/1Password/shell-plugins/sdk/schema/fieldname"
)

func APIToken() schema.CredentialType {
	return schema.CredentialType{
		Name:          credname.APIToken,
		DocsURL:       sdk.URL("https://docs.railway.app/guides/cli#authenticating-with-railway"),
		ManagementURL: sdk.URL("https://railway.app/account/tokens"),
		Fields: []schema.CredentialField{
			{
				Name:                fieldname.Token,
				MarkdownDescription: "Token used to authenticate to Railway.",
				Secret:              true,
				Composition: &schema.ValueComposition{
					Charset: schema.Charset{
						Uppercase: true,
						Lowercase: true,
						Digits:    true,
						Specific:  []rune{'-'},
					},
				},
			},
		},
		DefaultProvisioner: railwayProvisioner{},
		Importer: importer.TryAll(
			importer.TryAllEnvVars(fieldname.Token, "RAILWAY_API_TOKEN"),
			TryRailwayConfigFile("~/.railway/config.json"),
		),
	}
}

type railwayProvisioner struct{}

func (p railwayProvisioner) Description() string {
	return "Provision Railway API token via the RAILWAY_API_TOKEN environment variable."
}

func (p railwayProvisioner) Provision(ctx context.Context, in sdk.ProvisionInput, out *sdk.ProvisionOutput) {
	out.AddEnvVar("RAILWAY_API_TOKEN", in.ItemFields[fieldname.Token])
}

func (p railwayProvisioner) Deprovision(ctx context.Context, in sdk.DeprovisionInput, out *sdk.DeprovisionOutput) {
	// Environment variables are wiped automatically when the process exits.
}

func TryRailwayConfigFile(path string) sdk.Importer {
	return importer.TryFile(path, func(ctx context.Context, contents importer.FileContents, in sdk.ImportInput, out *sdk.ImportAttempt) {
		var config RailwayConfig
		if err := contents.ToJSON(&config); err != nil {
			out.AddError(err)
			return
		}

		token := config.User.AccessToken
		if token == "" {
			token = config.User.Token
		}
		if token == "" {
			return
		}

		out.AddCandidate(sdk.ImportCandidate{
			Fields: map[sdk.FieldName]string{
				fieldname.Token: token,
			},
		})
	})
}

type RailwayConfig struct {
	User RailwayUser `json:"user"`
}

type RailwayUser struct {
	Token       string `json:"token"`
	AccessToken string `json:"accessToken"`
}
