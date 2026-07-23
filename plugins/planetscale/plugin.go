package planetscale

import (
	"github.com/1Password/shell-plugins/sdk"
	"github.com/1Password/shell-plugins/sdk/schema"
)

func New() schema.Plugin {
	return schema.Plugin{
		Name: "planetscale",
		Platform: schema.PlatformInfo{
			Name:     "PlanetScale",
			Homepage: sdk.URL("https://planetscale.com"),
		},
		Credentials: []schema.CredentialType{
			AccessToken(),
		},
		Executables: []schema.Executable{
			PlanetScaleCLI(),
		},
	}
}
