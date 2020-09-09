package errors

import (
	"errors"
	"fmt"
	"log"

	"gopkg.in/src-d/go-git.v4"
)

var (
	// ErrUntrustedContributor is thrown when a contributor is not trusted
	ErrUntrustedContributor = errors.New("Contributor not found in list of trusted contributors")

	// ErrConflictingStatements is thrown when two staments are not independent and cannot be merged with the current policy
	ErrConflictingStatements = errors.New("Conflicting statements")

	// ErrNonIndependentStatements is thrown when two staments are not independent
	ErrNonIndependentStatements = errors.New("Non-independent statements")

	// ErrNothingToReconcile is thrown when two staments are independent and no reconciliation is needed
	ErrNothingToReconcile = errors.New("Statements are independent, nothing to reconcile")
)

var (
	// ErrConfigBackendRequired is thrown when no backend is supplied in a configuration
	ErrConfigBackendRequired = errors.New("Backend is required in sync configuration")

	// ErrConfigValidationFailed is thrown when the validation of the configuration fails
	ErrConfigValidationFailed = errors.New("Sync configuration validation failed")

	// ErrConfigVersionNotDefined is thrown when no API version is specified in a configuration
	ErrConfigVersionNotDefined = errors.New("ApiVersion not defined in configuration file")

	// ErrConfigInvalidImportRegex is thrown when an invalid import regex is specified in a configuration
	ErrConfigInvalidImportRegex = errors.New("Invalid import regex")

	// ErrConfigInvalidExportRegex is thrown when an invalid export regex is specified in a configuration
	ErrConfigInvalidExportRegex = errors.New("Invalid export regex")

	// ErrConfigPolicyMissing is thrown when no policy is specified in a configuration
	// TODO: rename to ErrConfigPolicyMissing, the choice of using a default needs not be
	// hardcoded here, so the term 'default' should not be used
	ErrConfigPolicyMissing = errors.New("Policy not set")

	// ErrConfigUnknownPolicy is thrown when an unknown/invalid policy is specified in a configuration
	ErrConfigUnknownPolicy = errors.New("Unknown policy listed in policies")

	// ErrConfigInvalidSourceURL is thrown when a source repository is specified without a valid URL
	ErrConfigInvalidSourceURL = errors.New("Source does not have a repo associated")

	// ErrConfigInvalid is used to signal any configuration error that is not covered by the other config errors
	ErrConfigInvalid = errors.New("Configuration is invalid")
)

// CheckErr verifies the type of error and choses to display a warning
// message or end the process
func CheckErr(e error) {
	if errors.Is(e, git.NoErrAlreadyUpToDate) {
		//fmt.Println("    already up to date, skipping pull")

	} else if errors.Is(e, ErrConflictingStatements) {
		fmt.Println("    contradicting statements, soft merge failed")
	} else if e != nil {
		log.Fatal(e)
	}
}

// PrintErr logs the error
func PrintErr(e error) {
	log.Println(e.Error())
}
