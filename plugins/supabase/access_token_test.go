package supabase

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
				fieldname.Token: "example-supabase-access-token-for-tests-only",
			},
			ExpectedOutput: sdk.ProvisionOutput{
				Environment: map[string]string{
					"SUPABASE_ACCESS_TOKEN": "example-supabase-access-token-for-tests-only",
				},
			},
		},
	})
}

func TestAccessTokenImporter(t *testing.T) {
	plugintest.TestImporter(t, AccessToken().Importer, map[string]plugintest.ImportCase{
		"environment": {
			Environment: map[string]string{
				"SUPABASE_ACCESS_TOKEN": "example-supabase-access-token-for-tests-only",
			},
			ExpectedCandidates: []sdk.ImportCandidate{
				{
					Fields: map[sdk.FieldName]string{
						fieldname.Token: "example-supabase-access-token-for-tests-only",
					},
				},
			},
		},
		"access token file": {
			Files: map[string]string{
				"~/.supabase/access-token": plugintest.LoadFixture(t, "access-token"),
			},
			ExpectedCandidates: []sdk.ImportCandidate{
				{
					Fields: map[sdk.FieldName]string{
						fieldname.Token: "example-supabase-access-token-for-tests-only",
					},
				},
			},
		},
	})
}
