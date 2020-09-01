package tasks

import (
	"os"

	"github.com/rs/zerolog/log"

	"github.com/sap/project-kb/kaybee/internal/conf"
	"github.com/sap/project-kb/kaybee/internal/model"
	"github.com/sap/project-kb/kaybee/internal/repository"
)

// MergeTask is the task that performs merging of statements, reconciling any
// conflicts using a set of pre-defined policies.
type MergeTask struct {
	policy  model.Policy
	sources []conf.SourceV1
}

// NewMergeTask constructs a new MergeTask
func NewMergeTask() (mergeTask *MergeTask) {
	mt := MergeTask{}
	return &mt
}

// WithPolicy sets the policy to be used to merge sources
func (t *MergeTask) WithPolicy(p conf.Policy) *MergeTask {
	log.Trace().Str("policy", string(p)).Msg("Adding")
	switch p {
	case conf.Strict:
		t.policy = model.NewStrictPolicy()
		break
	case conf.Soft:
		t.policy = model.NewSoftPolicy()
		break
	default:
		log.Fatal().Str("policy", string(p)).Msg("Invalid merge policy")
	}
	return t
}

// WithSources sets the sources to be merged
func (t *MergeTask) WithSources(sources []conf.SourceV1) *MergeTask {
	t.sources = sources
	return t
}

func (t *MergeTask) validate() (ok bool) {
	if (t.policy == model.Policy{}) {
		log.Fatal().Msg("Invalid merge policy")
	}
	if len(t.sources) < 1 {
		log.Fatal().Msg("No sources to merge")
	}
	return true
}

// Execute performs the actual merge task and returns true on success
func (t *MergeTask) Execute() (success bool) {
	log.Trace().Msg("Attempting merge")
	t.validate()

	statementsToMerge := make(map[string][]model.Statement)
	inputStatementCount := 0
	// collect statements from each source

	for _, source := range t.sources {
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
		Int("n_sources", len(t.sources)).
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
