// Copyright © 2019 - 2020, SAP. All rights reserved.

// Package conf contains code related to the configuration of the tool, which in turns
// specifies which upstream sources to fetch statements from, which sources are trusted,
// and how to merge statements according to one or more strategies
package conf

import "strings"

// "log"
// "os"
// "github.com/sap/project-kb/kaybee/internal/errors"
// homedir "github.com/mitchellh/go-homedir"

// "github.com/spf13/viper"
// "regexp"

// A Configuration encapsulates the relevant fields
// of configurations objects. This is used to hide the different configuration schema
// versions an provide a general API. This is the type that is ready everywere in the
// other packages.
type Configuration struct {
	version        string
	backend        string
	exportDenylist []string
	sources        []Source
	policies       []Policy
	export         []ExportScript
}

// A Source represents a remote repository in which vulnerability statements are stored
type Source struct {
	Repo   string `yaml:"repo"`
	Branch string `yaml:"branch"`
	Signed bool   `yaml:"signed"`
	Rank   int    `yaml:"rank"`
}

// A Policy determines how statements from different source repositories are
// to be merged (reconciled, when conflicting)
type Policy int

// Enumeration of the existing policy names
const (
	None Policy = iota
	Strict
	Soft
	Latest
	Oldest
)

// PolicyFromString converts a policy name into a Policy instance
func PolicyFromString(p string) Policy {
	p = strings.ToLower(p)
	switch p {
	case "strict":
		return Strict
	case "soft":
		return Soft
	case "latest":
		return Latest
	case "oldest":
		return Oldest
	}
	return None
}

func (p Policy) String() string {
	switch p {
	case Strict:
		return "Strict"
	case Soft:
		return "Soft"
	case Latest:
		return "Latest"
	case Oldest:
		return "Oldest"
	}
	return "None"
}

// ExportScript defines how to generate import scripts for a set of statements
type ExportScript struct {
	Target   string
	Filename string
	Pre      string
	Each     string
	Post     string
}

// Version returns the configuration schema version
func (c *Configuration) Version() string {
	return c.version
}

// Sources returns the sources (as a slice)
func (c *Configuration) Sources() []Source {
	return c.sources
}

// Validate checks consistency of configuration
func (c *Configuration) Validate() (ok bool, err error) {
	return true, nil
}

// Backend returns the backend from which to export
func (c *Configuration) Backend() string {
	return c.backend
}

// Policies returns the Policies from which to export
func (c *Configuration) Policies() []Policy {
	return c.policies
}

// ExportScripts returns the ExportScripts to generate
func (c *Configuration) ExportScripts() []ExportScript {
	return c.export
}

// ExportDenylist returns the ExportScripts to generate
func (c *Configuration) ExportDenylist() []string {
	return c.exportDenylist
}
