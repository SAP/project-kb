// Copyright © 2019 - 2020, SAP. All rights reserved.

package cmd

import (
	"fmt"

	"github.com/sap/project-kb/kaybee/internal/conf"
	"github.com/sap/project-kb/kaybee/internal/tasks"
	"github.com/spf13/cobra"
	// "github.com/sap/project-kb/kaybee/internal/goal"
)

// TODO make constructor method, as in ExportCmd, for testability

// mergeCmd represents the merge command
var mergeCmd = &cobra.Command{
	Use:   "merge",
	Short: "Merges statements from local clones of upstream source repositories",
	Long: `(CAUTION! OBSOLETE DESCRIPTION) Displays from a list of different source repositories a table of
cves which are possibly conflicting, attempts a soft merge and displays
each as mergeable or not along with the conflicting slices.

	kbsync merge -r [REPO_URL_1] -r [REPO_URL_2] -r ...
`,
	Run: doMerge,
}

var (
	repos           []string
	skipPull        bool
	mergePolicyName string
)

func init() {
	rootCmd.AddCommand(mergeCmd)

	// mergeCmd.Flags().StringSliceVarP(&repos, "repo", "r", []string{}, "repositories to diff")
	// mergeCmd.Flags().BoolVarP(&signed, "signed", "s", false, "Ignore unsigned commits")
	mergeCmd.Flags().BoolVarP(&skipPull, "skip-pull", "s", false, "Do not pull from remote repositories (only use their local copies)")
	mergeCmd.Flags().StringVarP(&mergePolicyName, "policy", "p", "strict", "Merge policy (default: strict")

}

func doMerge(cmd *cobra.Command, args []string) {
	if verbose {
		fmt.Println("Merging statements...")
	}

	if skipPull {
		if verbose {
			fmt.Println("Skipping pull, only local clones will be considered")
		}
	} else {
		doPull(cmd, args)
	}

	t := tasks.NewMergeTask().
		WithPolicy(conf.PolicyFromString(mergePolicyName)).
		WithSources(configuration.Sources())

	t.Verbose(verbose)
	t.Execute()

	if verbose {
		fmt.Println("Merge completed")
	}

}
