package repository

import (
	"fmt"
	"log"
	"path"
	"time"

	"gopkg.in/src-d/go-git.v4"
	"gopkg.in/src-d/go-git.v4/plumbing"
	"gopkg.in/src-d/go-git.v4/plumbing/object"

	"github.com/gookit/color"
	"github.com/schollz/progressbar/v2"

	"github.com/sap/project-kb/kaybee/internal/model"
	// "github.com/sap/project-kb/kaybee/pkg/util"
	"net/url"
	"path/filepath"
	"strings"

	"github.com/sap/project-kb/kaybee/internal/errors"
	"github.com/sap/project-kb/kaybee/internal/filesystem"
	"gopkg.in/yaml.v2"

	"io/ioutil"
)

// A Repository is a source of Statements
type Repository struct {
	URL     string          `yaml:"url"`
	Branch  string          `yaml:"branch"`
	Path    string          `yaml:"path"`
	Repo    *git.Repository `yaml:"repo"`
	Tree    *object.Tree    `yaml:"tree"`
	KeyRing []string
	// this is used to determine if statement signatures have to be checked
	Strict bool
	Rank   int
}

// NewRepository creates a new client and updates the appropriate path
func NewRepository(URL string, branch string, strict bool, rank int, targetDir string) Repository {
	r := Repository{}
	r.URL = URL
	r.Branch = branch
	r.Strict = strict
	r.Rank = rank

	var err error

	r.Path, _ = r.getRepoPath()
	r.Path = path.Join(targetDir, r.Path)

	if filesystem.IsDir(r.Path) {
		r.Repo, err = git.PlainOpen(r.Path)
		errors.CheckErr(err)

		// fetches head of the appropriate branch
		head, err := r.Repo.Head()
		errors.CheckErr(err)

		//  hashes the commit to get commit tree
		commit, err := r.Repo.CommitObject(head.Hash())
		errors.CheckErr(err)
		r.Tree, err = commit.Tree()
		errors.CheckErr(err)

		r.FetchKeyRing()
	}
	return r
}

// FetchKeyRing gets all available public GPG keys
func (r *Repository) FetchKeyRing() {
	if err := filesystem.CreateDir(filesystem.GetKeyPath(r.Path)); err == nil {
		keys, werr := filesystem.GetPubKey(filesystem.GetKeyPath(r.Path))
		errors.CheckErr(werr)
		r.KeyRing = keys
	}
}

// Pull attempts to pull the latest version of the origin remote
func (r *Repository) Pull() {
	w, err := r.Repo.Worktree()
	errors.CheckErr(err)
	refName := plumbing.ReferenceName(fmt.Sprintf("refs/heads/%s", r.Branch))
	errors.CheckErr(w.Pull(&git.PullOptions{
		ReferenceName: refName,
	}))
}

// Fetch creates and initializes a git repository if required
// from a given url and directory path. The clone is storage based
// and not memory based in order to avoid multiple clones required
// for consecutive executions
func (r *Repository) Fetch(verbose bool) {
	var err error
	if verbose {
		color.Info.Prompt("Cloning remote repository %s ...", r.URL)
	}
	if !filesystem.IsDir(r.Path) {
		refName := plumbing.ReferenceName(fmt.Sprintf("refs/heads/%s", r.Branch))
		r.Repo, err = git.PlainClone(r.Path, false, &git.CloneOptions{
			URL:           r.URL,
			ReferenceName: refName,
			SingleBranch:  true,
		})
		errors.CheckErr(err)
	} else {
		if verbose {
			color.Info.Prompt("Local clone exist, trying to update it")
		}
		r.Repo, err = git.PlainOpen(r.Path)
		errors.CheckErr(err)
		r.Pull()
	}

	// this is used to know when a repository was last updated; based on
	// this information, the "purge" command removes repositories according to
	// the configured retention period
	r.resetPullTimestamp()

	// fetches head of the appropriate branch
	head, err := r.Repo.Head()
	errors.CheckErr(err)

	//  hashes the commit to get commit tree
	commit, err := r.Repo.CommitObject(head.Hash())
	errors.CheckErr(err)
	r.Tree, err = commit.Tree()
	errors.CheckErr(err)

	if verbose {
		// updates the public approved keyrings
		color.Info.Prompt("Fetching keys")
	}
	r.FetchKeyRing()

	if verbose {
		color.Info.Prompt("Repository updated successfully.")
	}
}

// Statements returns a slice of statements from the commit tree of the repository
func (r *Repository) Statements() ([]model.Statement, error) {
	s := []model.Statement{}
	// log.Println("    collecting statements")

	files, _ := ioutil.ReadDir(r.Path + "/" + filesystem.DataPath)

	bar := progressbar.NewOptions(
		len(files),
		progressbar.OptionSetWidth(50),
		progressbar.OptionSetRenderBlankState(true),
		progressbar.OptionSetPredictTime(false),
	)
	// bar.Describe(fmt.Sprintf("---------\n"))

	if err := r.Tree.Files().ForEach(func(f *object.File) error {
		bar.Add(1)
		if _, vulnID, _, valid := filesystem.ParsePath(f.Name); valid {
			// log.Println("    processing ", string(f.Name))
			fnameLen := len(f.Name)
			if f.Name[fnameLen-5:fnameLen] != ".yaml" {
				color.Warn.Prompt("    skipping non-yaml file: " + f.Name)
				return nil
			}
			commitIter, err := r.Repo.Log(&git.LogOptions{FileName: &f.Name, Order: git.LogOrderCommitterTime})
			if err != nil {
				return err
			}

			result := model.Statement{}
			data, err := ioutil.ReadFile(filepath.Join(r.Path, f.Name))
			if err != nil {
				color.Error.Prompt("Error reading " + filepath.Join(r.Path, f.Name))
				return err
			}

			if err := yaml.Unmarshal(data, &result); err != nil {
				color.Error.Prompt("Error when unmarshaling " + filepath.Join(r.Path, f.Name))
				return err
			}

			if o, err := commitIter.Next(); o != nil && err == nil {
				if r.Strict {
					if !r.VerifyCommit(o) {
						color.Error.Prompt("Commit {%s} failed gpg key verification, ignored", o.Hash)
						return nil
					}
				}

				result.VulnerabilityID = vulnID

				metadata := model.Metadata{
					Origin: r.URL,
					// Timestamp:  o.Author.When.Unix(),
					// Signature:  o.PGPSignature,
					Branch:     r.Branch,
					OriginRank: r.Rank,
					LocalPath:  path.Join(r.Path, f.Name),
				}
				// result.Metadata = metadata

				// for i := range result.Fixes {
				// 	result.Fixes[i].Metadata = metadata
				// }

				// for i := range result.Notes {
				// 	result.Notes[i].Metadata = metadata
				// }

				result.Metadata = metadata
				s = append(s, result)
			}
		}
		return nil
	}); err != nil {
		return s, err
	}
	return s, nil
}

// VerifyCommit checks if the commit signature corresponds to any available keys
func (r *Repository) VerifyCommit(o *object.Commit) bool {
	for _, k := range r.KeyRing {
		valid, err := o.Verify(k)
		if err != nil {
			return false
		}
		if valid != nil {
			return true
		}
	}
	return false
}

// getRepoPath returns the dir safe name of a repository
func (r *Repository) getRepoPath() (string, error) {

	parsedURL, err := url.Parse(r.URL)
	if err != nil {
		return "", err
	}

	if parsedURL.Scheme == "file" {
		return filepath.Join(".", strings.ReplaceAll(parsedURL.Path[1:], "/", ".")+"_"+r.Branch), nil
	}

	if parsedURL.Path == "" {
		log.Fatal("The source URL is invalid: " + r.URL)
	}

	return filepath.Join(parsedURL.Host + "_" + strings.ReplaceAll(parsedURL.Path[1:], "/", ".") + "_" + r.Branch), nil
}

// getLicensePath returns the disk path of the license
func (r *Repository) getLicensePath() (string, error) {
	repo, err := r.getRepoPath()
	if err != nil {
		return "", err
	}
	return filepath.Join(repo), nil
}

func (r *Repository) resetPullTimestamp() {
	ts := fmt.Sprint(time.Now().Unix())

	fileName := path.Join(r.Path, ".pull_timestamp")
	err := ioutil.WriteFile(fileName, []byte(ts), 0600)
	if err != nil {
		log.Fatal(err)
	}

}
