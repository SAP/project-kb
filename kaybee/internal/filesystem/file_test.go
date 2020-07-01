package filesystem

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestParsePath(t *testing.T) {
	// Test path parsing successful
	if _, _, _, valid := ParsePath("statements/cve_1234/statement.yaml"); !valid {
		t.Errorf("path [data/cve_1234/statement.yaml] should be valid during parsing")
	}

	// Test invalid length path
	if _, _, _, valid := ParsePath("ichbinfrog/statement.yaml"); valid {
		t.Errorf("path [ichbinfrog/statement.yaml] should be invalid")
	}

	// Test invalid root dir parse
	if _, _, _, valid := ParsePath("root/invalid_root/cve_1234/statement.yaml"); valid {
		t.Errorf("path [root/invalid_root/cve_1234/statement.yaml] should be invalid")
	}
}

func TestGetPath(t *testing.T) {
	// Test keypath
	keyPath := GetKeyPath("tests")
	if keyPath != "tests/"+KeyPath {
		t.Errorf("keypath [%s] is malformed, should be tests/%s", keyPath, KeyPath)
	}

	// Test datapath
	dataPath := GetDataPath("ichbinfrog")
	if dataPath != "ichbinfrog/"+DataPath {
		t.Errorf("datapath [%s] is malformed, should be ichbinfrog/%s", dataPath, DataPath)
	}
}

// func TestGetPubKey(t *testing.T) {
// 	// Test valid key
// 	keys, err := GetPubKey(GetKeyPath("../tests"))
// 	if err != nil || len(keys) == 0 {
// 		t.Errorf("failed to parse key [tests/signature/test.asc]")
// 	}

// 	if len(keys) != 1 {
// 		t.Errorf("error with filter, only one key should be present")
// 	}
// }

func TestDirUtils(t *testing.T) {
	// File
	if IsDir("../../testdata/steady/all_bugs.json") {
		t.Errorf("../../testdata/steady/all_bugs.json should be recognised as a file")
	}
	// Dir
	if !IsDir("../../testdata/steady") {
		t.Errorf("../../testdata/steady should be recognised as a directory")
	}
	// Non existent
	if IsDir("holla") {
		t.Errorf("holla should not be recognised as a directory")
	}

	os.RemoveAll("tests/test_dir")
	// Non recursive non existent directory
	if err := CreateDir("tests/test_dir"); err != nil {
		t.Errorf("createdir should succeed with path tests/test_dir")
	}
	// // Recursive creation
	// if err := CreateDir("tests/test_dir/test_dir/test_dir"); err == nil {
	// 	t.Errorf("createdir should fail with path tests/test_dir/test_dir/test_dir when recursive false")
	// }
	os.RemoveAll("tests/test_dir")
}

func TestIsFile(t *testing.T) {
	assert.True(t, IsFile("/etc/issue"))
	assert.False(t, IsFile("/etc/issue/fdsafjfas"))
}

// func TestURLParse(t *testing.T) {
// 	if _, err := GetRepoPath("https://github.com/sap/project-kb/kaybee", "."); err != nil {
// 		t.Error(err)
// 	}
// }
