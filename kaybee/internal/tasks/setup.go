package tasks

import (
	"fmt"
	"log"
	"os"

	"github.com/gobuffalo/packr"
	"github.com/sap/project-kb/kaybee/internal/filesystem"
)

// SetupTask is the task that performs merging of statements, reconciling any
// conflicts using a set of pre-defined policies.
type SetupTask struct {
	BaseTask
	force       bool
	interactive bool
}

// NewSetupTask constructs a new MergeTask
func NewSetupTask() *SetupTask {

	t := SetupTask{
		force:       false,
		interactive: false,
	}
	return &t
}

// WithForceMode sets the flag that controls whether the setup should be done even
// if a configuration file is already existing (in which case, it will be overwritten)
func (t *SetupTask) WithForceMode() *SetupTask {
	t.force = true
	return t
}

// WithInteractiveMode enables interactive mode
func (t *SetupTask) WithInteractiveMode(im bool) *SetupTask {
	t.interactive = im
	return t
}

// Execute performs the actual task and returns true on success
func (t *SetupTask) Execute() (success bool) {
	fmt.Println("[+] Running Setup task")

	t.validate()

	const path string = "./kaybeeconf.yaml"

	// check if file exists
	if filesystem.FileExists(path) {
		// force := ctx.Get("force").(bool)
		if t.force {
			var err = os.Remove(path)
			if err != nil {
				log.Fatal("There was an error removing the existing file")
			}
		} else {
			fmt.Printf("The configuration file %s exists. Re-run with the -f flag to overwrite it.\n", path)
			log.Fatal("Aborting")
		}
	}

	f, err := os.Create(path)
	if err != nil {
		fmt.Printf("Failed to create file: %s", path)
	}
	f.Close()

	f, err = os.OpenFile(path, os.O_RDWR, 0644)
	if err != nil {
		log.Fatalf("%v", err)
	}
	defer f.Close()

	configFileContent := getDefaultConfig()
	_, err = f.WriteString(configFileContent)
	if err != nil {
		log.Fatalf("%v", err)
	}

	// Save file changes.
	err = f.Sync()
	if err != nil {
		log.Fatalf("%v", err)
	}

	fmt.Println("[+] Setup task completed")
	return true
}

func getDefaultConfig() string {
	box := packr.NewBox("./data")

	s, err := box.FindString("default_config.yaml")
	if err != nil {
		log.Fatal(err)
	}
	return s
}
