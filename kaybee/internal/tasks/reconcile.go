package tasks

import (
	"fmt"

	"github.com/sap/project-kb/kaybee/internal/conf"
)

// ReconcileTask is the task that performs merging of statements, reconciling any
// conflicts using a set of pre-defined policies.
type ReconcileTask struct {
	BaseTask
	Sources         []conf.Source
	VulnerabilityID string
}

// NewReconcileTask constructs a new ReconcileTask
func NewReconcileTask() (mergeTask *ReconcileTask) {

	mt := ReconcileTask{}
	return &mt
}

func (t *ReconcileTask) validate() (ok bool) {

	return true
}

// Execute performs the actual task and returns true on success
func (t *ReconcileTask) Execute() (success bool) {

	if t.verbose {
		fmt.Println("Reconciling statements for vulnerability ID: " + t.VulnerabilityID)
		fmt.Println("Using sources:")
		for _, s := range t.Sources {
			fmt.Println(s)
		}
	}

	t.validate()

	fmt.Println("WARNING: Reconcile task not implemented yet!")

	return true
}
