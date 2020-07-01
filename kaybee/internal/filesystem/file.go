package filesystem

import (
	"io/ioutil"
	// "net/url"
	"os"
	"path/filepath"
	"strings"
)

const (
	// DataPath is the root folder for cve storage
	DataPath = "statements"

	// KeyPath is the directory in which keys are stored
	KeyPath = "signature"

	// LicensePath is the name of the license file stored in local
	LicensePath = "LICENSE"
)

// GetKeyPath returns the key path joined with the base path
func GetKeyPath(path string) string {
	return filepath.Join(path, KeyPath)
}

// GetDataPath returns the data path joined with the base path
func GetDataPath(path string) string {
	return filepath.Join(path, DataPath)
}

// GetPubKey walks the path and finds all gpg public armored keys in
// that directory (that ends with .asc)
func GetPubKey(path string) ([]string, error) {
	keys := []string{}

	if err := filepath.Walk(path, func(path string, info os.FileInfo, err error) error {
		if info.Mode().IsRegular() {
			if filepath.Ext(path) == ".asc" {
				if key, err := ioutil.ReadFile(path); err == nil {
					keys = append(keys, string(key))
				}
			}
		}
		return nil
	}); err != nil {
		return keys, err
	}

	return keys, nil
}

// CreateDir makes a directory at the given path
func CreateDir(path string) error {
	if err := os.MkdirAll(path, 0750); err != nil {
		return err
	}
	return nil
}

// IsDir checks if a directory exists
func IsDir(path string) bool {
	if fi, err := os.Stat(path); !os.IsNotExist(err) {
		if fi.Mode().IsDir() {
			return true
		}
		return false
	}
	return false
}

// IsFile checks if a file exists
func IsFile(path string) bool {
	if fi, err := os.Stat(path); !os.IsNotExist(err) {
		if err != nil {
			return false
		}
		if fi.Mode().IsRegular() {
			return true
		}
		return false
	}
	return false
}

// ParsePath returns the root, bugID, filename
// of the given filepath
func ParsePath(path string) (string, string, string, bool) {
	parts := strings.Split(filepath.ToSlash(path), "/")
	if len(parts) < 3 || parts[len(parts)-3] != DataPath {
		return "", "", "", false
	}

	return strings.Join(parts[:len(parts)-3], ""), parts[len(parts)-2], parts[len(parts)-1], true
}

// // GetRepoPath returns the dir safe name of a repository
// func GetRepoPath(path string, root string) (string, error) {
// 	u, err := url.Parse(path)
// 	if err != nil {
// 		return "", err
// 	}
// 	return filepath.Join(root, u.Hostname()+strings.ReplaceAll(u.Path, "/", ".")), nil
// }

// SplitPath returns the directory name and the filename of a given path
func SplitPath(path string) (string, string) {
	return filepath.Split(path)
}

// // GetLicensePath returns the disk path of the license
// func GetLicensePath(URL string, root string) (string, error) {
// 	repo, err := GetRepoPath(URL, root)
// 	if err != nil {
// 		return "", err
// 	}
// 	return filepath.Join(repo), nil
// }

// CreateFile creates a file in a given path if it does not exist
func CreateFile(path string) (*os.File, error) {
	return os.OpenFile(path, os.O_WRONLY|os.O_CREATE, 0600)
}

// FileExists checks if a file exists at the specified path
func FileExists(path string) bool {
	var _, err = os.Stat(path)
	if os.IsNotExist(err) {
		return false
	}
	return true
}
