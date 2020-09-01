// Package tasks contains all implementations of tasks; these are instantiated
// and run from the main package
package tasks

// "github.com/sap/project-kb/kaybee/internal/conf"

// The Task interface defines the behaviour that all tasks must implement
type Task interface {
	Execute() (success bool)
	validate() (ok bool)
}
