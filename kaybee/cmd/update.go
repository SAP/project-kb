// Copyright © 2019 - 2020, SAP. All rights reserved.

package cmd

import (
	"fmt"
	"log"

	"github.com/rhysd/go-github-selfupdate/selfupdate"
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
	fmt.Println("Running update...")

	latest, ok, e := selfupdate.DetectLatest("sap/project-kb")
	if e != nil {
		log.Fatal("error: ", e)
	}

	if ok {
		fmt.Println("Latest version available: " + latest.URL)
	} else {
		fmt.Println("Could not check the latest available version, you may want to retry later.")
	}

	fmt.Println("Update completed")

}
