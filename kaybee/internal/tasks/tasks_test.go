package tasks

import (
	"log"
	"testing"

	"github.com/sap/project-kb/kaybee/internal/conf"
)

//
// FIXTURES
//
func getConfig() conf.Configuration {
	p, err := conf.NewParser("../../testdata/conf/kaybeeconf.yaml")
	// p.SetConfigFile()
	if err != nil {
		return conf.Configuration{}
	}
	c, _ := p.Parse()
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
	pullTask := NewPullTask().WithSources(conf.Sources())
	pullTask.Execute()

	task := NewMergeTask().
		WithPolicy(conf.Policies()[0]).
		WithSources(conf.Sources())
	task.Execute()
}

//
// PULL
//
func TestPullTask(t *testing.T) {
	conf := getConfig()
	log.Printf("config: %v", conf)

	pullTask := NewPullTask().WithSources(conf.Sources())
	pullTask.Execute()
}
