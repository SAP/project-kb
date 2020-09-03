package conf

// ------------------------
// --- Configuration V1 ---
// ------------------------

// A ConfigV1 represents a configuration object conforming to V.1 of the
// configuration schema
type ConfigV1 struct {
	Version        string         `yaml:"apiVersion"`
	Backend        string         `yaml:"backend"`
	ExportDenylist []string       `yaml:"export_denylist"` // for some reason export_denylist is not a good key (Viper bug?)
	Sources        SourcesV1      `yaml:"sources"`
	Policies       []Policy       `yaml:"policies"`
	Export         []ExportScript `yaml:"export"`
}

// A SourcesV1 represents a remote repository in which vulnerability statements are stored
type SourcesV1 []struct {
	Repo   string `yaml:"repo"`
	Branch string `yaml:"branch"`
	Signed bool   `yaml:"signed"`
	Rank   int    `yaml:"rank"`
}

func (s SourcesV1) Length() int {
	return len(s)
}

func (c ConfigV1) Validate() bool {
	return true
}

func (c ConfigV1) GetPolicies() []Policy {
	return c.Policies
}

func (c ConfigV1) GetSources() SourceIterator {
	return c.Sources
}

func (c ConfigV1) GetBackend() string {
	return c.Backend
}

func (c ConfigV1) GetExportDenyList() []string {
	return c.ExportDenylist
}

func (c ConfigV1) GetExportScripts() []ExportScript {
	return c.Export
}
