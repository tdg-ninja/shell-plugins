package supabase

import (
	"github.com/1Password/shell-plugins/sdk"
	"github.com/1Password/shell-plugins/sdk/needsauth"
	"github.com/1Password/shell-plugins/sdk/schema"
	"github.com/1Password/shell-plugins/sdk/schema/credname"
)

func SupabaseCLI() schema.Executable {
	return schema.Executable{
		Name:    "Supabase CLI",
		Runs:    []string{"supabase"},
		DocsURL: sdk.URL("https://supabase.com/docs/reference/cli"),
		NeedsAuth: needsauth.IfAll(
			needsauth.NotForHelpOrVersion(),
			needsauth.NotWithoutArgs(),
			needsauth.NotWhenContainsArgs("login"),
			needsauth.NotWhenContainsArgs("logout"),
			needsauth.NotWhenContainsArgs("--help"),
			needsauth.NotWhenContainsArgs("--version"),
		),
		Uses: []schema.CredentialUsage{
			{
				Name: credname.AccessToken,
			},
		},
	}
}
