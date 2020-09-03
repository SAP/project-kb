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
	Sources         SourcesV2
	Policies        []Policy
}

// A SourcesV2 represents a remote repository in which vulnerability statements are stored
type SourcesV2 map[int]struct {
	Repo   string `yaml:"repo"`
	Branch string `yaml:"branch"`
	Signed bool   `yaml:"signed"`
}

func (s SourcesV2) Length() int {
	return len(s)
}

func (c ConfigV2) Validate() bool {
	return true
}
func (c ConfigV2) GetPolicies() []Policy {
	return c.Policies
}

func (c ConfigV2) GetSources() SourceIterator {
	return c.Sources
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
