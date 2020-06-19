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
	Sources         map[int]Source
	Policies        []Policy
	//ParsedExport   map[string][]*regexp.Regexp
}

// A Source represents a remote repository in which vulnerability statements are stored
type Source struct {
	Repo   string `yaml:"repo"`
	Branch string `yaml:"branch"`
	Signed bool   `yaml:"signed"`
}

// A Policy determines how statements from different source repositories are
// to be merged (reconciled, when conflicting)
type Policy int

// Validate the configuration
func (c ConfigV2) Validate() (result bool) {
	if c.Backend == "" {
		return false
	}

	return true
}

// GetSources returns a slice of sources
func (c *ConfigV2) GetSources() map[int]Source {
	return c.Sources
}
