package supabase

import (
	"github.com/1Password/shell-plugins/sdk"
	"github.com/1Password/shell-plugins/sdk/schema"
)

func New() schema.Plugin {
	return schema.Plugin{
		Name: "supabase",
		Platform: schema.PlatformInfo{
			Name:     "Supabase",
			Homepage: sdk.URL("https://supabase.com"),
		},
		Credentials: []schema.CredentialType{
			AccessToken(),
		},
		Executables: []schema.Executable{
			SupabaseCLI(),
		},
	}
}
