package conf

import (
	"fmt"
	"testing"

	"github.com/sap/project-kb/kaybee/internal/errors"
	"gotest.tools/assert"
)

func TestParser(t *testing.T) {
	c, err := ParseConfiguration("../../testdata/conf/kaybeeconf.yaml")
	if err != nil {
		return
	}
	fmt.Printf("\n%+v\n", c)
	assert.Equal(t, len(c.GetSources()), 2, "Found wrong number of sources")
}

func TestParserNoVersion(t *testing.T) {
	_, err := ParseConfiguration("../../testdata/conf/kaybeeconf_noversion.yaml")
	if err != nil {
		return
	}
	assert.Equal(t, err, errors.ErrConfigVersionNotDefined)
}

func TestParserMalformed1(t *testing.T) {
	_, err := ParseConfiguration("../../testdata/conf/sample_kbsync_malformed.yaml")
	if err != nil {
		return
	}
	assert.Equal(t, err, errors.ErrConfigVersionNotDefined)
}

// func TestImportScriptSettings(t *testing.T) {
// 	p, err := NewParser()
// 	p.SetConfigFile("../../myconfig")
// 	if err != nil {
// 		return
// 	}
// 	c, _ := p.Parse()
// 	fmt.Printf("%v", c)
// }
