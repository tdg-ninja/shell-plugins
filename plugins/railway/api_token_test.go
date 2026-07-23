package railway

import (
	"testing"

	"github.com/1Password/shell-plugins/sdk"
	"github.com/1Password/shell-plugins/sdk/plugintest"
	"github.com/1Password/shell-plugins/sdk/schema/fieldname"
)

func TestAPITokenProvisioner(t *testing.T) {
	plugintest.TestProvisioner(
		t, APIToken().DefaultProvisioner, map[string]plugintest.ProvisionCase{
			"default": {
				ItemFields: map[sdk.FieldName]string{
					fieldname.Token: "fake-railway-api-token-abc123def456ghi789EXAMPLE",
				},
				ExpectedOutput: sdk.ProvisionOutput{
					Environment: map[string]string{
						"RAILWAY_API_TOKEN": "fake-railway-api-token-abc123def456ghi789EXAMPLE",
					},
				},
			},
		},
	)
}

func TestAPITokenImporter(t *testing.T) {
	plugintest.TestImporter(
		t, APIToken().Importer, map[string]plugintest.ImportCase{
			"RAILWAY_API_TOKEN environment variable": {
				Environment: map[string]string{
					"RAILWAY_API_TOKEN": "fake-railway-api-token-abc123def456ghi789EXAMPLE",
				},
				ExpectedCandidates: []sdk.ImportCandidate{
					{
						Fields: map[sdk.FieldName]string{
							fieldname.Token: "fake-railway-api-token-abc123def456ghi789EXAMPLE",
						},
					},
				},
			},
			"config file": {
				Files: map[string]string{
					"~/.railway/config.json": plugintest.LoadFixture(t, "config.json"),
				},
				ExpectedCandidates: []sdk.ImportCandidate{
					{
						Fields: map[sdk.FieldName]string{
							fieldname.Token: "fake-railway-api-token-abc123def456ghi789EXAMPLE",
						},
					},
				},
			},
		},
	)
}
