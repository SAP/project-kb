/*
Copyright © 2020 NAME HERE <EMAIL ADDRESS>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package cmd

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strconv"
	"time"

	"path/filepath"

	"github.com/spf13/cobra"
)

const (
	secondsInADay int64 = 3600 * 24
)

var (
	maxRetention int
)

// purgeCmd represents the purge command
var purgeCmd = &cobra.Command{
	Use:   "purge",
	Short: "Remove all local clones of remote sources",
	Long: `Remove all local clones of remote sources. This command should be run
	periodically to ensure that data from 3rd party sources, especially personal data
	about the committers of those sources, is not retained for longer than necessary.

	The '-r' flag can be used to specify the maximum number of days a local clone can
	remain in the filesystem without being refreshed (with the 'pull' command) before
	it is considered stale and therefore deleted. If the flag is not set (of if its value
	is set to 0), all local clones are removed, regardless of their age.`,
	Run: func(cmd *cobra.Command, args []string) {
		doPrune(args)
	},
}

func init() {
	rootCmd.AddCommand(purgeCmd)
	purgeCmd.Flags().IntVarP(&maxRetention, "retention", "r", 0, "Purge local clones older than the specified number of days (default: purge all)")
}

func doPrune(args []string) {
	fmt.Println("Purging old data")

	if maxRetention < 0 {
		log.Fatal("Retention duration should be a non-negative value.")
	}

	repositoryDirs, err := ioutil.ReadDir(".kaybee/repositories/")
	if err != nil {
		log.Fatal(err)
	}

	if len(repositoryDirs) < 1 {
		fmt.Println("No local clones found, nothing to purge.")
		return
	}

	for _, d := range repositoryDirs {
		if d.IsDir() {
			timestampFile, err := os.Open(filepath.Join(".kaybee/repositories/", d.Name(), ".pull_timestamp"))
			if err != nil {
				log.Fatal(err)
			}
			defer timestampFile.Close()

			b, _ := ioutil.ReadAll(timestampFile)
			tsInt64, _ := strconv.ParseInt(string(b), 0, 64)
			// fmt.Printf("%d", tsInt64)
			ageInDays := int((time.Now().Unix() - tsInt64) / secondsInADay)
			if ageInDays >= maxRetention {
				if verbose {
					fmt.Printf("  Removing %s (age: %d days)\n", d.Name(), ageInDays)
					os.RemoveAll(filepath.Join(".kaybee/repositories/", d.Name()))
				}
			} else {
				if verbose {
					fmt.Printf("  Keeping %s (age: %d days)\n", d.Name(), ageInDays)
				}
			}
		}
	}
	fmt.Println("Purging completed")
}
