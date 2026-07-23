package planetscale

import (
	"context"
	"strings"

	"github.com/1Password/shell-plugins/sdk"
	"github.com/1Password/shell-plugins/sdk/importer"
	"github.com/1Password/shell-plugins/sdk/schema"
	"github.com/1Password/shell-plugins/sdk/schema/credname"
	"github.com/1Password/shell-plugins/sdk/schema/fieldname"
)

func AccessToken() schema.CredentialType {
	return schema.CredentialType{
		Name:          credname.AccessToken,
		DocsURL:       sdk.URL("https://github.com/planetscale/cli#authentication"),
		ManagementURL: sdk.URL("https://app.planetscale.com/settings/tokens"),
		Fields: []schema.CredentialField{
			{
				Name:                fieldname.Token,
				MarkdownDescription: "Access token used to authenticate to PlanetScale.",
				Secret:              true,
				Composition: &schema.ValueComposition{
					Length: 43,
					Prefix: "pscale_oauth_",
					Charset: schema.Charset{
						Lowercase: true,
						Uppercase: true,
						Digits:    true,
					},
				},
			},
		},
		DefaultProvisioner: planetscaleProvisioner{},
		Importer: importer.TryAll(
			importer.TryEnvVarPair(defaultEnvVarMapping),
			TryPlanetScaleAccessTokenFile("~/.config/planetscale/access-token"),
		),
	}
}

var defaultEnvVarMapping = map[string]sdk.FieldName{
	"PLANETSCALE_API_TOKEN": fieldname.Token,
}

type planetscaleProvisioner struct{}

func (p planetscaleProvisioner) Description() string {
	return "PlanetScale CLI access token provisioner"
}

func (p planetscaleProvisioner) Provision(ctx context.Context, input sdk.ProvisionInput, output *sdk.ProvisionOutput) {
	output.AddArgs("--api-token", input.ItemFields[fieldname.Token])
}

func (p planetscaleProvisioner) Deprovision(ctx context.Context, input sdk.DeprovisionInput, output *sdk.DeprovisionOutput) {
	// No-op
}

func TryPlanetScaleAccessTokenFile(path string) sdk.Importer {
	return importer.TryFile(path, func(ctx context.Context, contents importer.FileContents, in sdk.ImportInput, out *sdk.ImportAttempt) {
		accessToken := strings.TrimSpace(contents.ToString())
		if accessToken == "" {
			return
		}

		out.AddCandidate(sdk.ImportCandidate{
			Fields: map[sdk.FieldName]string{
				fieldname.Token: accessToken,
			},
		})
	})
}
