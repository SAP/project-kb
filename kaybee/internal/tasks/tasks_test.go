package tasks

import (
	"log"
	"testing"

	"github.com/sap/project-kb/kaybee/internal/conf"
)

//
// FIXTURES
//
func getConfig() conf.Config {
	c, _ := conf.ParseConfiguration("../../testdata/conf/kaybeeconf.yaml")
	return c
}

//
// EXPORT
//
// func TestExporterPool(t *testing.T) {

// 	vulasBackend := "https://vulas.tools.sap/"

// 	ep, err := NewExporterPool(vulasBackend, 2, 4, map[string][]*regexp.Regexp{})
// 	if err != nil {
// 		t.Error(err)
// 	}

// 	results := ep.Run()

// 	if len(results) == 0 {
// 		t.Error("no results, error fetching data")
// 	}

// 	// fmt.Printf("%v", results)
// 	marshaled, _ := yaml.Marshal(results)
// 	fmt.Printf(string(marshaled))

// }

//
// MERGE
//
func TestMergeTask(t *testing.T) {
	conf := getConfig()
	log.Printf("config: %v", conf)

	// merge needs pull!
	pullTask := NewPullTask().WithSources(conf.GetSources())
	pullTask.Execute()

	task := NewMergeTask().
		WithPolicy(conf.GetPolicies()[0]).
		WithSources(conf.GetSources())
	task.Execute()
}

//
// PULL
//
func TestPullTask(t *testing.T) {
	conf := getConfig()
	log.Printf("config: %v", conf)

	pullTask := NewPullTask().WithSources(conf.GetSources())
	pullTask.Execute()
}
