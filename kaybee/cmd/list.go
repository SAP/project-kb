// +build ignore
// Copyright © 2019 - 2020, SAP. All rights reserved.

package cmd

import (
	"github.com/sap/project-kb/kaybee/internal/goal"
	"github.com/spf13/cobra"
)

// listCmd represents the list command
var listCmd = &cobra.Command{
	Use:   "list",
	Short: "List elements from the vulnerability document store",
	Long: `List elements from the vulnerability document store following
this overall declaration:

	list [FLAGS] [TYPE] [TYPE_SPECIFIC_ARGUMENTS]

- sources from a config file: list sources [CONFIG_FILE]
- bugs stored in a certain repository: list bugs [REPO_URL]
`,
	Args: cobra.MinimumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
	},
}

var listBugsCmd = &cobra.Command{
	Use:   "bugs",
	Short: "List bugs stored in an instance of the CVE document store",
	Long: `List bugs stored in an instance of the CVE document store. This command
fetches the latest version of the document store hosted in a given URL and temporarily
stores it in the given path.

kaybee list bugs [FLAGS] [REPO_URL] [CACHE_PATH(optional)]
`,
	Args: cobra.MinimumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		c := &goal.ListBugs{}
		c.New("", verbose)
		c.Add(args[0], branch, cacheDir, signed)
		c.Run()
	},
}

var listRepoCmd = &cobra.Command{
	Use:   "sources",
	Short: "List sources declared in a sync file",
	Long:  `List sources declared in a sync file`,
	Args:  cobra.MinimumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		// c := &goal.ListSources{}
		// c.New(args[0])
		// c.Run()
	},
}

var listSigCmd = &cobra.Command{
	Use:   "signatures",
	Short: "List public keys declared in a sync file",
	Long:  `List public keys declared in a sync file`,
	Args:  cobra.MinimumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		c := &goal.ListBugs{}
		c.New(args[0], verbose)

		// for _, s := range c.List.Base.Parser.GetSources() {
		// 	c.Add(s.Repo, s.Branch, cacheDir, signed)
		// }

		c.PubKeys()
	},
}

var (
	repo, branch string
	signed       bool
)

func init() {
	rootCmd.AddCommand(listCmd)
	listCmd.AddCommand(listRepoCmd)

	listBugsCmd.Flags().BoolVarP(&signed, "signed", "s", false, "Ignores all unsigned commits")
	listBugsCmd.Flags().StringVarP(&repo, "repo", "r", "", "url of the vulnkb")
	listBugsCmd.Flags().StringVarP(&branch, "branch", "b", "master", "branch storing the vulnkb")
	listCmd.AddCommand(listBugsCmd)

	listCmd.AddCommand(listSigCmd)
}
