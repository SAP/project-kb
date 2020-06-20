package conf

import (
	// "github.com/joho/godotenv"
	// "log"
	"fmt"
	"testing"

	"github.com/magiconair/properties/assert"
	"github.com/sap/project-kb/kaybee/internal/errors"
)

// func init() {
// 	err := godotenv.Load()
// 	if err != nil {
// 		log.Fatal("error loading .env file")
// 	}
// }

func TestParser(t *testing.T) {

	p, err := NewParser("../../testdata/conf/kaybeeconf.yaml")
	if err != nil {
		return
	}
	c, _ := p.Parse()
	fmt.Printf("\n%v\n", c)

	// isValid := c.Validate()
	fmt.Printf("\nVersion: %s\n", c.Version())

	assert.Equal(t, len(c.Sources()), 2, "Found wrong number of sources")
}

func TestParserNoVersion(t *testing.T) {

	p, err := NewParser("../../testdata/conf/kaybeeconf_noversion.yaml")
	if err != nil {
		return
	}
	_, err = p.Parse()
	assert.Equal(t, err, errors.ErrConfigVersionNotDefined)
}

func TestParserMalformed1(t *testing.T) {

	p, err := NewParser("../../testdata/conf/sample_kbsync_malformed.yaml")
	if err != nil {
		return
	}
	_, err = p.Parse()
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
