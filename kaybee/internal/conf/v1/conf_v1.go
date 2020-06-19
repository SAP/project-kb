package v1

// ------------------------
// --- Configuration V1 ---
// ------------------------

// A Configuration represents a configuration object conforming to V.1 of the
// configuration schema
type Configuration struct {
	Version        string         `yaml:"apiVersion"`
	Backend        string         `yaml:"backend"`
	ExportDenylist []string       `yaml:"exportdenylist"` // for some reason export_denylist is not a good key (Viper bug?)
	Sources        []Source       `yaml:"sources"`
	Policies       []string       `yaml:"policies"`
	Export         []ExportScript `yaml:"export"`
}

// A Source represents a remote repository in which vulnerability statements are stored
type Source struct {
	Repo   string `yaml:"repo"`
	Branch string `yaml:"branch"`
	Signed bool   `yaml:"signed"`
	Rank   int    `yaml:"rank"`
}

// ExportScript defines how to generate import scripts for a set of statements
type ExportScript struct {
	Target   string `yaml:"target"`
	Filename string `yaml:"filename"`
	Pre      string `yaml:"pre"`
	Each     string `yaml:"each"`
	Post     string `yaml:"post"`
}
