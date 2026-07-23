package planetscale

import (
	"github.com/1Password/shell-plugins/sdk"
	"github.com/1Password/shell-plugins/sdk/needsauth"
	"github.com/1Password/shell-plugins/sdk/schema"
	"github.com/1Password/shell-plugins/sdk/schema/credname"
)

func PlanetScaleCLI() schema.Executable {
	return schema.Executable{
		Name:    "PlanetScale CLI",
		Runs:    []string{"pscale"},
		DocsURL: sdk.URL("https://github.com/planetscale/cli"),
		NeedsAuth: needsauth.IfAll(
			needsauth.NotForHelpOrVersion(),
			needsauth.NotWithoutArgs(),
			needsauth.NotWhenContainsArgs("auth"),
			needsauth.NotWhenContainsArgs("signup"),
			needsauth.NotWhenContainsArgs("completion"),
			needsauth.NotWhenContainsArgs("--api-token"),
		),
		Uses: []schema.CredentialUsage{
			{
				Name: credname.AccessToken,
			},
		},
	}
}
