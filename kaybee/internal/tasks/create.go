package tasks

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/contrib/static"
	"github.com/gin-gonic/gin"

	"github.com/sap/project-kb/kaybee/internal/browser"
	"github.com/sap/project-kb/kaybee/internal/model"
)

// CreateTask is the task that performs merging of statements, reconciling any
// conflicts using a set of pre-defined policies.
type CreateTask struct {
	BaseTask
	enableGUI bool
	vulnID    string
}

// GUIPort is the port (on localhost) on which the Statement creation wizart
// will be exposed
const GUIPort string = "3001"

// NewCreateTask constructs a new MergeTask
func NewCreateTask() *CreateTask {

	t := CreateTask{
		enableGUI: false,
	}
	return &t
}

// WithGUI enables a graphical UI to create the new statement
func (t *CreateTask) WithGUI(enableGUI bool) *CreateTask {
	t.enableGUI = enableGUI
	return t
}

// WithVulnerabilityID sets the ID of the vulnerability we're creating a statement for
func (t *CreateTask) WithVulnerabilityID(id string) *CreateTask {
	t.vulnID = id
	return t
}

// Execute performs the actual task and returns true on success
func (t *CreateTask) Execute() (success bool) {

	t.validate()
	if t.enableGUI {

		// Set the router as the default one shipped with Gin
		router := gin.Default()

		// Serve frontend static files
		router.Use(static.Serve("/", static.LocalFile("ui/build", true)))

		// Setup route group for the API
		api := router.Group("/api")
		{
			api.GET("/", func(c *gin.Context) {
				c.JSON(http.StatusOK, gin.H{
					"message": "pong",
				})
			})
		}

		browser.OpenURL("http://localhost:" + GUIPort)

		// Start and run the server
		router.Run(":" + GUIPort)

	} else {
		// var vulnID = "CVE-xxxx-yyyy"
		var statement = model.Statement{
			VulnerabilityID: t.vulnID,
			Notes: []model.Note{
				{
					Links: []string{
						"https://..............",
						"https://.......................",
					},
					Text: "Some note about " + t.vulnID,
				},
			},
			Fixes: []model.Fix{
				{
					ID: "BRANCH_IDENTIFIER",
					Commits: []model.Commit{
						{
							ID:            "COMMIT_ID",
							RepositoryURL: "https://github.com/.......",
						},
						{
							ID:            "COMMIT_ID",
							RepositoryURL: "https://github.com/.......",
						},
					},
				},
				{
					ID: "ANOTHER_BRANCH",
					Commits: []model.Commit{
						{
							ID:            "COMMIT_ID",
							RepositoryURL: "https://github.com/.......",
						},
						{
							ID:            "COMMIT_ID",
							RepositoryURL: "https://github.com/.......",
						},
					},
				},
			},
		}

		statement.ToFile("./kaybee-new-statements")
		fmt.Printf("The file './kaybee-new-statements/" + t.vulnID + "/statement.yaml' has been created.\n")
		fmt.Printf("With your favourite text editor, modify it as you see fit, then run the following command:\n\n")
		fmt.Printf("  kaybee export --target steady --from ./kaybee-new-statements/\n\n")
		fmt.Printf("That will create the script 'steady.sh' that is ready to be executed to import data into the Steady backend.\n")
	}

	return true
}
