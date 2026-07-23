package planetscale

import (
	"testing"

	"github.com/1Password/shell-plugins/sdk"
	"github.com/1Password/shell-plugins/sdk/plugintest"
	"github.com/1Password/shell-plugins/sdk/schema/fieldname"
)

func TestAccessTokenProvisioner(t *testing.T) {
	plugintest.TestProvisioner(t, AccessToken().DefaultProvisioner, map[string]plugintest.ProvisionCase{
		"default": {
			ItemFields: map[sdk.FieldName]string{
				fieldname.Token: "pscale_oauth_0123456789abcdef0123456789ab",
			},
			ExpectedOutput: sdk.ProvisionOutput{
				CommandLine: []string{"--api-token", "pscale_oauth_0123456789abcdef0123456789ab"},
			},
		},
	})
}

func TestAccessTokenImporter(t *testing.T) {
	plugintest.TestImporter(t, AccessToken().Importer, map[string]plugintest.ImportCase{
		"environment": {
			Environment: map[string]string{
				"PLANETSCALE_API_TOKEN": "pscale_oauth_0123456789abcdef0123456789ab",
			},
			ExpectedCandidates: []sdk.ImportCandidate{
				{
					Fields: map[sdk.FieldName]string{
						fieldname.Token: "pscale_oauth_0123456789abcdef0123456789ab",
					},
				},
			},
		},
		"access token file": {
			Files: map[string]string{
				"~/.config/planetscale/access-token": plugintest.LoadFixture(t, "access-token"),
			},
			ExpectedCandidates: []sdk.ImportCandidate{
				{
					Fields: map[sdk.FieldName]string{
						fieldname.Token: "pscale_oauth_0123456789abcdef0123456789ab",
					},
				},
			},
		},
	})
}
