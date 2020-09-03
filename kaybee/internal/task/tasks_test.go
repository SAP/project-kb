package task

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
	pullTask := &Pull{
		Sources: conf.GetSources(),
	}
	pullTask.Execute()

	task := &Merge{
		Sources:      conf.GetSources(),
		PolicyString: conf.GetPolicies()[0],
	}
	task.Execute()
}

//
// PULL
//
func TestPullTask(t *testing.T) {
	conf := getConfig()
	log.Printf("config: %v", conf)

	pullTask := &Pull{
		Sources: conf.GetSources(),
	}
	pullTask.Execute()
}
