package render

import (
	"context"

	"github.com/1Password/shell-plugins/sdk"
	"github.com/1Password/shell-plugins/sdk/importer"
	"github.com/1Password/shell-plugins/sdk/provision"
	"github.com/1Password/shell-plugins/sdk/schema"
	"github.com/1Password/shell-plugins/sdk/schema/credname"
	"github.com/1Password/shell-plugins/sdk/schema/fieldname"
)

func APIKey() schema.CredentialType {
	return schema.CredentialType{
		Name:          credname.APIKey,
		DocsURL:       sdk.URL("https://render.com/docs/cli#non-interactive-mode"),
		ManagementURL: sdk.URL("https://dashboard.render.com/account/api-keys"),
		Fields: []schema.CredentialField{
			{
				Name:                fieldname.APIKey,
				MarkdownDescription: "API Key used to authenticate to Render.",
				Secret:              true,
				Composition: &schema.ValueComposition{
					Charset: schema.Charset{
						Lowercase: true,
						Uppercase: true,
						Digits:    true,
						Symbols:   true,
					},
				},
			},
		},
		DefaultProvisioner: provision.EnvVars(defaultEnvVarMapping),
		Importer: importer.TryAll(
			importer.TryEnvVarPair(defaultEnvVarMapping),
			TryRenderConfigFile("~/.render/cli.yaml"),
		),
	}
}

var defaultEnvVarMapping = map[string]sdk.FieldName{
	"RENDER_API_KEY": fieldname.APIKey,
}

func TryRenderConfigFile(path string) sdk.Importer {
	return importer.TryFile(
		path,
		func(ctx context.Context, contents importer.FileContents, in sdk.ImportInput, out *sdk.ImportAttempt) {
			var config Config
			if err := contents.ToYAML(&config); err != nil {
				out.AddError(err)
				return
			}

			if config.API.Key == "" {
				return
			}

			out.AddCandidate(
				sdk.ImportCandidate{
					Fields: map[sdk.FieldName]string{
						fieldname.APIKey: config.API.Key,
					},
				},
			)
		},
	)
}

type Config struct {
	API APIConfig `yaml:"api"`
}

type APIConfig struct {
	Key string `yaml:"key"`
}
