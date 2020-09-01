package tasks

import (
	"github.com/rs/zerolog/log"

	"github.com/sap/project-kb/kaybee/internal/conf"
	"github.com/sap/project-kb/kaybee/internal/repository"
)

// PullTask is the task that performs merging of statements, reconciling any
// conflicts using a set of pre-defined policies.
type PullTask struct {
	sources []conf.SourceV1
}

// NewPullTask constructs a new MergeTask
func NewPullTask() *PullTask {
	t := PullTask{}
	return &t
}

// WithSources sets the sources to be merged
func (t *PullTask) WithSources(sources []conf.SourceV1) *PullTask {
	t.sources = sources
	return t
}

func (t *PullTask) validate() (ok bool) {
	if len(t.sources) < 1 {
		log.Fatal().Msg("No sources to pull")
	}
	return true
}

// Execute performs the actual task and returns true on success
func (t *PullTask) Execute() (success bool) {
	// fmt.Println("[+] Running pull task")

	// cfg, _ := ctx.Get("configuration").(conf.Configuration)
	// verbose := ctx.Get("verbose").(bool)
	// c := ctx.Get("configuration").(conf.Configuration)
	// for _, v := range c.Sources() {
	// 	fmt.Printf("%s\n", v.Repo)
	// }

	t.validate()
	for _, src := range t.sources {
		log.Info().Str("repo", src.Repo).Msg("Pulling")
		repository := repository.NewRepository(src.Repo, src.Branch, true, src.Rank, ".kaybee/repositories")
		repository.Fetch()
		log.Info().Str("repo", src.Repo).Msg("Finished pulling")
	}

	// fmt.Println("[+] Pull task completed")
	return true
}
