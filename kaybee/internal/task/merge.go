package task

import (
	"os"

	"github.com/rs/zerolog/log"

	"github.com/sap/project-kb/kaybee/internal/conf"
	"github.com/sap/project-kb/kaybee/internal/model"
	"github.com/sap/project-kb/kaybee/internal/repository"
)

// Merge is the task that performs merging of statements, reconciling any
// conflicts using a set of pre-defined policies.
type Merge struct {
	PolicyString conf.Policy
	policy       model.Policy
	Sources      conf.SourceIterator
}

func (t *Merge) mustValidate() {
	switch t.PolicyString {
	case conf.Strict:
		t.policy = model.NewStrictPolicy()
		break
	case conf.Soft:
		t.policy = model.NewSoftPolicy()
		break
	default:
		log.Fatal().Str("policy", string(t.PolicyString)).Msg("Invalid merge policy")
	}
	if (t.policy == model.Policy{}) {
		log.Fatal().Msg("Invalid merge policy")
	}
	if t.Sources.Length() < 1 {
		log.Fatal().Msg("No sources to merge")
	}
}

// Execute performs the actual merge task and returns true on success
func (t *Merge) Execute() (success bool) {
	log.Trace().Msg("Attempting merge")
	t.mustValidate()

	statementsToMerge := make(map[string][]model.Statement)
	inputStatementCount := 0

	// collect statements from each source
	switch sources := t.Sources.(type) {
	case conf.SourcesV1:
		for _, source := range sources {
			log.Trace().Str("source", source.Repo).Str("branch", source.Branch).Msg("Collection vuln statements")
			repository := repository.NewRepository(source.Repo, source.Branch, false, source.Rank, ".kaybee/repositories")
			statements, err := repository.Statements()
			if err != nil {
				log.Fatal().Err(err).Msg("Failed to fetch statements")
			}
			for _, stmt := range statements {
				statementsToMerge[stmt.VulnerabilityID] = append(statementsToMerge[stmt.VulnerabilityID], stmt)
				inputStatementCount++
			}
		}
		break
	case conf.SourcesV2:
		for _, source := range sources {
			log.Trace().Str("source", source.Repo).Str("branch", source.Branch).Msg("Collection vuln statements")
			repository := repository.NewRepository(source.Repo, source.Branch, false, 0, ".kaybee/repositories")
			statements, err := repository.Statements()
			if err != nil {
				log.Fatal().Err(err).Msg("Failed to fetch statements")
			}
			for _, stmt := range statements {
				statementsToMerge[stmt.VulnerabilityID] = append(statementsToMerge[stmt.VulnerabilityID], stmt)
				inputStatementCount++
			}
		}
		break
	}
	log.Trace().Msg("Reconciling statements")
	// TODO adjust terminology: reduce, merge, reconcile....
	mergedStatements, mergeLog, err := t.policy.Reduce(statementsToMerge)
	if err != nil {
		log.Error().Err(err).Msg("Failed to merge")
	}
	// fmt.Printf("Merged:\n%v", mergedStatements)
	os.RemoveAll(".kaybee/merged/")

	for _, st := range mergedStatements {
		if len(st) != 1 {
			log.Fatal().Msg("Failed to merge multiple statements into a single vulnerability")
		}
		st[0].ToFile(".kaybee/merged/")
	}
	log.Trace().
		Int("n_initial_statements", inputStatementCount).
		Int("n_sources", t.Sources.Length()).
		Int("n_result_statements", len(mergedStatements)).
		Msg("Merge operations")
	mergeLog.Dump(".kaybee/merged/")

	// if verbose {
	// 	fmt.Println("Merge log:")
	// 	for _, logEntry := range mergeLog.Entries() {
	// 		fmt.Printf("%v\n", logEntry)
	// 	}
	// }

	return true
}
