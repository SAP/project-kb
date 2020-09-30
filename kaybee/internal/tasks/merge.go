package tasks

import (
	"fmt"
	"log"
	"os"

	"github.com/sap/project-kb/kaybee/internal/conf"
	"github.com/sap/project-kb/kaybee/internal/model"
	"github.com/sap/project-kb/kaybee/internal/repository"
)

// MergeTask is the task that performs merging of statements, reconciling any
// conflicts using a set of pre-defined policies.
type MergeTask struct {
	BaseTask
	policy  model.Policy
	sources []conf.Source
}

// NewMergeTask constructs a new MergeTask
func NewMergeTask() (mergeTask *MergeTask) {

	mt := MergeTask{}
	return &mt
}

// WithPolicy sets the policy to be used to merge sources
func (t *MergeTask) WithPolicy(p conf.Policy) *MergeTask {
	switch p {
	case conf.Strict:
		if t.verbose {
			fmt.Println("Using policy: STRICT")
		}
		t.policy = model.NewStrictPolicy()
	case conf.Soft:
		if t.verbose {
			fmt.Println("Using policy: SOFT")
		}
		t.policy = model.NewSoftPolicy()
	default:
		log.Fatalf("Invalid merge policy -- ABORTING")
	}
	return t
}

// WithSources sets the sources to be merged
func (t *MergeTask) WithSources(sources []conf.Source) *MergeTask {
	t.sources = sources
	return t
}

func (t *MergeTask) validate() (ok bool) {
	if (t.policy == model.Policy{}) {
		log.Fatalln("Invalid policy. Aborting.")
		return false
	}
	if len(t.sources) < 1 {
		log.Fatalln("No sources to merge. Aborting.")
		return false
	}

	return true
}

// Execute performs the actual merge task and returns true on success
func (t *MergeTask) Execute() (success bool) {

	if t.verbose {
		fmt.Println("Merging...")
	}

	t.validate()

	statementsToMerge := make(map[string][]model.Statement)

	inputStatementCount := 0

	// collect statements from each source
	for _, source := range t.sources {
		if t.verbose {
			fmt.Printf("\nCollecting vulnerability statements from %s (%s)\n", source.Repo, source.Branch)
		}

		repository := repository.NewRepository(source.Repo, source.Branch, false, source.Rank, ".kaybee/repositories")

		statements, err := repository.Statements()
		if err != nil {
			log.Fatal(err)
		}

		for _, stmt := range statements {
			statementsToMerge[stmt.VulnerabilityID] = append(statementsToMerge[stmt.VulnerabilityID], stmt)
			inputStatementCount++
		}
	}

	fmt.Printf("\n")
	if t.verbose {
		fmt.Printf("Reconciling statements...\n")
	}

	// TODO adjust terminology: reduce, merge, reconcile....
	mergedStatements, mergeLog, err := t.policy.Reduce(statementsToMerge)
	if err != nil {
		fmt.Printf("Could not merge: %v", err)
	}

	// fmt.Printf("Merged:\n%v", mergedStatements)
	os.RemoveAll(".kaybee/merged/")

	for _, st := range mergedStatements {
		// log.Printf("%+v\n", st)
		if len(st) != 1 {
			log.Fatal("WEIRD! After merging, there are still multiple statements for the same vulnerability!")
		}
		st[0].ToFile(".kaybee/merged/")
	}

	fmt.Printf("Merged %d sources (%d statements): yielded %d statements.\n", len(t.sources), inputStatementCount, len(mergedStatements))

	os.MkdirAll(".kaybee/merged/", os.ModePerm)
	mergeLog.Dump(".kaybee/merged/")

	// if verbose {
	// 	fmt.Println("Merge log:")
	// 	for _, logEntry := range mergeLog.Entries() {
	// 		fmt.Printf("%v\n", logEntry)
	// 	}
	// }

	return true
}
