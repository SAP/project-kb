// Copyright © 2019 - 2020, SAP. All rights reserved.

// Package conf contains code related to the configuration of the tool, which in turns
// specifies which upstream sources to fetch statements from, which sources are trusted,
// and how to merge statements according to one or more strategies
package conf

import (
	"io/ioutil"
	"path/filepath"

	homedir "github.com/mitchellh/go-homedir"
	"github.com/rs/zerolog/log"
	"github.com/sap/project-kb/kaybee/internal/errors"
	"github.com/sap/project-kb/kaybee/internal/filesystem"
	"gopkg.in/yaml.v2"
)

// A Policy determines how statements from different source repositories are
// to be merged (reconciled, when conflicting)
type Policy string

// Enumeration of the existing policy names
const (
	None   Policy = "none"
	Strict Policy = "strict"
	Soft   Policy = "soft"
	Latest Policy = "latest"
	Oldest Policy = "oldest"
)

type SourceIterator interface {
	Length() int
}

type Config interface {
	Validate() bool
	GetPolicies() []Policy
	GetSources() SourceIterator
	GetBackend() string
	GetExportDenyList() []string
	GetExportScripts() []ExportScript
}

// ExportScript defines how to generate import scripts for a set of statements
type ExportScript struct {
	Target   string `yaml:"target"`
	Filename string `yaml:"filename"`
	Pre      string `yaml:"pre"`
	Each     string `yaml:"each"`
	Post     string `yaml:"post"`
}

func ParseConfiguration(file string) (Config, error) {
	// Attempt to read files in a given set of paths
	// Find home directory. Required for Darwin compatibility
	home, err := homedir.Dir()
	if err != nil {
		log.Trace().Err(err).Msg("Failed to find home directory")
	}
	var data []byte
	var finalPath string
	for _, path := range []string{
		file,
		filepath.Join(".", file+".yaml"),
		filepath.Join(home, ".kaybee", file+".yaml"),
		filepath.Join("etc", "kaybee", file+".yaml"),
	} {
		if !filesystem.IsFile(path) {
			continue
		}
		data, err = ioutil.ReadFile(path)
		if err != nil {
			log.Error().Err(err).
				Str("path", path).
				Msg("Failed to read config file")
			continue
		}
		finalPath = path
	}
	if finalPath == "" {
		log.Error().Msg("Failed to read any config file")
		return nil, err
	}

	// Preliminary marshal to find version
	prelim := make(map[string]interface{})
	if err := yaml.Unmarshal(data, &prelim); err != nil {
		log.Error().Err(err).Str("path", finalPath).Msg("Failed to unmarshal")
		return nil, err
	}

	// Marshal according to configuration version
	if version, ok := prelim["apiVersion"]; ok {
		switch version {
		case "v1":
			conf := &ConfigV1{}
			err := yaml.Unmarshal(data, &conf)
			if err != nil {
				log.Error().Err(err).Msg("Failed to unmarshal to ConfigV1")
			}
			return conf, err
		case "v2":
			conf := &ConfigV2{}
			err := yaml.Unmarshal(data, &conf)
			if err != nil {
				log.Error().Err(err).Msg("Failed to unmarshal to ConfigV2")
			}
			return conf, err
		}
	}
	return nil, errors.ErrConfigVersionNotDefined
}
