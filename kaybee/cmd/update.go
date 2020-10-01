// Copyright © 2019 - 2020, SAP. All rights reserved.

package cmd

import (
	"fmt"
	"log"

	"github.com/blang/semver"
	"github.com/rhysd/go-github-selfupdate/selfupdate"
	"github.com/spf13/cobra"
)

var forceUpdate bool

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
	updateCmd.Flags().BoolVarP(&forceUpdate, "force", "f", false, "Upgrade to the latest version, if different from the one in use")
}

func doUpdate(cmd *cobra.Command, args []string) {
	fmt.Print("Checking new releases...\n")

	// fmt.Println("You currently have version: " + version)
	latest, ok, e := selfupdate.DetectLatest("sap/project-kb")
	if e != nil {
		log.Fatal("error: ", e)
	}

	if ok {
		latestSemVer := semver.MustParse(latest.Version.String())

		// // TESTING
		// version = "0.0.1"
		currentSemVer := semver.MustParse(version)
		// currentSemVer := semver.MustParse("0.1.1")

		if latestSemVer.Compare(currentSemVer) > 0 {
			fmt.Printf("Newer version detected\n")
			fmt.Println("Latest version available: " + latest.Version.String())
			fmt.Println("You are currently using: " + currentSemVer.String())

			if forceUpdate {
				fmt.Println("Please wait while downloading and upgrading to version " + latest.Version.String())
				newVersion, err := selfupdate.UpdateSelf(currentSemVer, "sap/project-kb")
				if err != nil {
					fmt.Println("Could not update to new version. Aborting.")
					return
				}
				fmt.Print("Done upgrading to version " + newVersion.Version.String())
			} else {
				fmt.Println("Please download it from: " + latest.URL)
				fmt.Println("or run 'kaybee update --force' to download and install automatically.")
			}
		} else {
			fmt.Println("You have the latest version.")
		}

	} else {
		fmt.Println("Could not check the latest available version, you may want to retry later.")
	}

}
