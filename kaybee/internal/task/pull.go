package task

import (
	"github.com/rs/zerolog/log"

	"github.com/sap/project-kb/kaybee/internal/conf"
	"github.com/sap/project-kb/kaybee/internal/repository"
)

// Pull is the task that performs merging of statements, reconciling any
// conflicts using a set of pre-defined policies.
type Pull struct {
	Sources conf.SourceIterator
}

func (t *Pull) mustValidate() {
	if t.Sources.Length() < 1 {
		log.Fatal().Msg("No sources to pull")
	}
}

// Execute performs the actual task and returns true on success
func (t *Pull) Execute() (success bool) {
	// fmt.Println("[+] Running pull task")

	// cfg, _ := ctx.Get("configuration").(conf.Configuration)
	// verbose := ctx.Get("verbose").(bool)
	// c := ctx.Get("configuration").(conf.Configuration)
	// for _, v := range c.Sources() {
	// 	fmt.Printf("%s\n", v.Repo)
	// }
	t.mustValidate()
	switch sources := t.Sources.(type) {
	case conf.SourcesV1:
		for _, src := range sources {
			log.Info().Str("repo", src.Repo).Msg("Pulling")
			repository := repository.NewRepository(src.Repo, src.Branch, true, src.Rank, ".kaybee/repositories")
			repository.Fetch()
			log.Info().Str("repo", src.Repo).Msg("Finished pulling")
		}
		break
	case conf.SourcesV2:
		for _, src := range sources {
			log.Info().Str("repo", src.Repo).Msg("Pulling")
			repository := repository.NewRepository(src.Repo, src.Branch, true, 0, ".kaybee/repositories")
			repository.Fetch()
			log.Info().Str("repo", src.Repo).Msg("Finished pulling")
		}
		break
	}
	// fmt.Println("[+] Pull task completed")
	return true
}
