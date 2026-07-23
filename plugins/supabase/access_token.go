package supabase

import (
	"context"
	"strings"

	"github.com/1Password/shell-plugins/sdk"
	"github.com/1Password/shell-plugins/sdk/importer"
	"github.com/1Password/shell-plugins/sdk/provision"
	"github.com/1Password/shell-plugins/sdk/schema"
	"github.com/1Password/shell-plugins/sdk/schema/credname"
	"github.com/1Password/shell-plugins/sdk/schema/fieldname"
)

var defaultEnvVarMapping = map[string]sdk.FieldName{
	"SUPABASE_ACCESS_TOKEN": fieldname.Token,
}

func AccessToken() schema.CredentialType {
	return schema.CredentialType{
		Name:          credname.AccessToken,
		DocsURL:       sdk.URL("https://supabase.com/docs/reference/cli/supabase-login"),
		ManagementURL: sdk.URL("https://supabase.com/dashboard/account/tokens"),
		Fields: []schema.CredentialField{
			{
				Name:                fieldname.Token,
				MarkdownDescription: "Access token used to authenticate to Supabase.",
				Secret:              true,
				Composition: &schema.ValueComposition{
					Prefix: "sbp_",
					Length: 44,
					Charset: schema.Charset{
						Lowercase: true,
						Digits:    true,
					},
				},
			},
		},
		DefaultProvisioner: provision.EnvVars(defaultEnvVarMapping),
		Importer: importer.TryAll(
			importer.TryEnvVarPair(defaultEnvVarMapping),
			TrySupabaseAccessTokenFile("~/.supabase/access-token"),
		),
	}
}

func TrySupabaseAccessTokenFile(path string) sdk.Importer {
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
