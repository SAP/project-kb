package conf

import (
	"path/filepath"

	homedir "github.com/mitchellh/go-homedir"
	"github.com/spf13/viper"

	"log"
	"os"

	confV1 "github.com/sap/project-kb/kaybee/internal/conf/v1"
	// confV2 "github.com/sap/project-kb/kaybee/internal/conf/v2"
	"github.com/sap/project-kb/kaybee/internal/errors"
)

// -----------------------------
// --- Configuration parsing ---
// -----------------------------

// const defaultConfigFileName string = "kaybeeconf"

// Parser is responsible for parsing the configuration file
// in order to generate a configuration object
type Parser struct {
	viper.Viper
}

// NewParser creates a new Parser and initializes the viper configuration
func NewParser(cfgFile string) (*Parser, error) {
	p := new(Parser)
	p.Viper = *viper.New()

	p.Viper.SetConfigName(cfgFile)
	p.Viper.SetConfigType("yaml")

	// Find home directory.
	home, err := homedir.Dir()
	if err != nil {
		log.Println(err)
		os.Exit(1)
	}

	// order matters!
	p.Viper.AddConfigPath(".") // first look for config in the working directory
	p.Viper.AddConfigPath(filepath.Join(home, ".kaybee"))
	p.Viper.AddConfigPath(home)           // then in the home
	p.Viper.AddConfigPath("/etc/kaybee/") // last in the global configuration

	// p.Viper.AutomaticEnv()

	return p, nil
}

// SetConfigFile allows to inject an additional config file
// overriding what was set previously
func (p *Parser) SetConfigFile(configFile string) {
	p.Viper.SetConfigFile(configFile)
}

// Parse parses the configuration file according to the version specified
// This method produces as output a Configuration object that hides the differences
// in the configuration schema versions. All the logic to handle different versions
// should be invisible to the client of Configuration instances.
func (p *Parser) Parse() (config Configuration, err error) {

	if err := p.Viper.ReadInConfig(); err != nil {
		log.Fatal("Config file missing or corrupted.")
	}

	m := make(map[string]interface{})
	if err := p.Viper.Unmarshal(&m); err != nil {
		return Configuration{}, err
	}

	// first detect the version of the configuration schema
	if version, ok := m["apiversion"]; ok {
		switch version {
		case "v1":
			c := &confV1.Configuration{}
			p.Viper.Unmarshal(&c)
			c.Version = "1.0"
			return parseV1(c), nil
		// case "v2":
		// 	c := &confV2.Configuration{}
		// 	p.Viper.Unmarshal(&c)
		// 	c.Version = "2.0"
		// 	return parseV2(c), nil
		// NOTE: TO ADD ANOTHER CONFIGURATION SCHEMA VERSION
		// Just add another case here and implement a corresponding parseVx()
		// function below, following the example of the existing parseV1()
		default:
			return Configuration{}, errors.ErrConfigVersionNotDefined
		}
	}

	// log.Fatalf("Invalid configuration, schema version is missing.")
	return Configuration{}, errors.ErrConfigVersionNotDefined
}

// this function maps the concrete syntax (version-specific) of the configuration
// file with the generic (version independent) Configuration structure
func parseV1(data *confV1.Configuration) Configuration {

	var (
		sources        []Source
		policies       []Policy
		exportScripts  []ExportScript
		exportDenylist []string
	)
	for _, s := range data.Sources {
		sources = append(sources, Source{
			Repo:   s.Repo,
			Branch: s.Branch,
			Signed: s.Signed,
			Rank:   s.Rank,
		})
	}

	for _, p := range data.Policies {
		// conversion is easy, policies are integers after all
		policies = append(policies, PolicyFromString(p))
	}

	for _, is := range data.Export {
		exportScripts = append(exportScripts, ExportScript{
			Filename: is.Filename,
			Pre:      is.Pre,
			Post:     is.Post,
			Target:   is.Target,
			Each:     is.Each,
		})
	}

	for _, pattern := range data.ExportDenylist {
		exportDenylist = append(exportDenylist, pattern)
	}

	conf := Configuration{
		version:        data.Version,
		backend:        data.Backend,
		sources:        sources,
		policies:       policies,
		export:         exportScripts,
		exportDenylist: exportDenylist,
	}
	return conf
}

// func parseV2(data *confV1.Configuration) Configuration{
// 	conf := Configuration{

// 	}
// 	return conf
// }
// // GetSources returns the sources of a given version of configuration
// func (p *Parser) GetSources() map[int]Source {
// 	switch p.Version {
// 	case "v1":
// 		return p.Config.(ConfigV1).ParsedSources
// 	}
// 	return nil
// }

// // GetPolicies returns the list of policy interfaces
// func (p *Parser) GetPolicies() []interface{} {
// 	switch p.Version {
// 	case "v1":
// 		return p.Config.(ConfigV1).ParsedPolicies
// 	}
// 	return nil
// }

// func (p *Parser) GetBackend() string {
// 	switch p.Version {
// 	case "v1":
// 		return p.Config.(ConfigV1).Backend
// 	}
// 	return ""
// }

// func (p *Parser) GetExportFilter() map[string][]*regexp.Regexp {
// 	switch p.Version {
// 	case "v1":
// 		return p.Config.(ConfigV1).ParsedExport
// 	}
// 	return nil
// }
