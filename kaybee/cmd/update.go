// Copyright © 2019 - 2020, SAP. All rights reserved.

package cmd

import (
	"fmt"

	"github.com/blang/semver/v4"
	"github.com/rhysd/go-github-selfupdate/selfupdate"
	"github.com/rs/zerolog/log"
	"github.com/spf13/cobra"
)

var updateCmd = &cobra.Command{
	Use:   "update",
	Short: "Creates a configuration, unless it exists already",
	Long: `(CAUTION! OBSOLETE DESCRIPTION) Displays from a list of different source repositories a table of
cves which are possibly conflicting, attempts a soft merge and displays
each as mergeable or not along with the conflicting slices.

	kbsync update [-i]
`,
	Run: doUpdate,
}

func init() {
	rootCmd.AddCommand(updateCmd)
	// updateCmd.Flags().BoolVarP(&interactive, "interactive", "i", false, "Interactive configuration")
	// updateCmd.Flags().BoolVarP(&force, "force", "f", false, "Force overwrite existing configuration file")
}

func doUpdate(cmd *cobra.Command, args []string) {
	fmt.Print("Checking new releases...\n")

	// fmt.Println("You currently have version: " + version)
	latest, ok, err := selfupdate.DetectLatest("sap/project-kb")
	if err != nil {
		log.Fatal().Err(err)
	}

	if ok {
		latestSemVer := semver.MustParse(latest.Version.String())
		currentSemVer := semver.MustParse(version)

		if latestSemVer.Compare(currentSemVer) > 0 {
			log.Info().Msg("New version detected")
			log.Info().Str("version", latest.Version.String()).Msg("Newer version available")
			log.Info().Str("url", latest.URL).Msg("Download it from")
		} else {
			log.Info().Str("version", latest.Version.String()).Msg("You have the latest version")
		}
	} else {
		log.Info().Msg("Could not check the latest available version, you may want to retry later.")
	}
}
