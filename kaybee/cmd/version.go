/*
Copyright © 2020 SAP
*/

package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

var (
	buildDate     string
	buildCommitID string
	version       string
)

// versionCmd represents the version command
var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Display version and build information",
	Long: `A longer description that spans multiple lines and likely contains examples
and usage of using your command. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	Run: func(cmd *cobra.Command, args []string) {
		printBanner()
		fmt.Println("Version:            " + version)
		fmt.Println("Build time:         " + buildDate)
		fmt.Println("Built from commit:  " + buildCommitID)
		fmt.Println("")
		doUpdate(cmd, args)
	},
}

func init() {
	rootCmd.AddCommand(versionCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// versionCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// versionCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}

func printBanner() {
	banner := `    __ __               ____
   / //_/____ _ __  __ / __ ) ___   ___
  / ,<  / __ ` + "`" + `// / / // __  |/ _ \ / _ \
 / /| |/ /_/ // /_/ // /_/ //  __//  __/
/_/ |_|\__,_/ \__, //_____/ \___/ \___/
             /____/` + "\n\n"

	fmt.Print(banner)
	fmt.Printf("                    by SAP Security Research\n\n")
	fmt.Printf("project \"KB\" -- https://sap.github.io/project-kb\n\n")
	fmt.Println("This is KayBee, a tool developed in project \"KB\", to create and maintain\n" +
		"a collaborative, distributed knowledge base about vulnerabilities of open-source software.\n")

}
