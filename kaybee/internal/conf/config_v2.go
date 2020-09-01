package conf

// ------------------------
// --- Configuration V2 ---
// ------------------------

// A ConfigV2 represents a configuration object conforming to V.2 of the
// configuration schema
type ConfigV2 struct {
	Version         string `yaml:"apiVersion"`
	Backend         string
	ExportBlacklist map[string][]string
	Sources         map[int]SourceV2
	Policies        []Policy
}

// A SourceV2 represents a remote repository in which vulnerability statements are stored
type SourceV2 struct {
	Repo   string `yaml:"repo"`
	Branch string `yaml:"branch"`
	Signed bool   `yaml:"signed"`
}

func (c ConfigV2) Validate() bool {
	return true
}
func (c ConfigV2) GetPolicies() []Policy {
	return c.Policies
}

func (c ConfigV2) GetSources() []SourceV1 {
	sources := []SourceV1{}
	for _, source := range c.Sources {
		sources = append(sources, SourceV1{
			Repo:   source.Repo,
			Branch: source.Branch,
			Signed: true,
			Rank:   0,
		})
	}
	return sources
}

func (c ConfigV2) GetBackend() string {
	return c.Backend
}

func (c ConfigV2) GetExportDenyList() []string {
	denyList := []string{}
	for _, deny := range c.ExportBlacklist {
		denyList = append(denyList, deny...)
	}
	return denyList
}

func (c ConfigV2) GetExportScripts() []ExportScript {
	return nil
}
