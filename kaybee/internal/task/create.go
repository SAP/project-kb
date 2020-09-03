package task

import (
	"net/http"
	"path/filepath"

	"github.com/gin-gonic/contrib/static"
	"github.com/gin-gonic/gin"
	"github.com/rs/zerolog/log"

	"github.com/sap/project-kb/kaybee/internal/browser"
	"github.com/sap/project-kb/kaybee/internal/model"
)

// Create is the task that performs merging of statements, reconciling any
// conflicts using a set of pre-defined policies.
type Create struct {
	EnableGUI bool
	VulnID    string
}

// GUIPort is the port (on localhost) on which the Statement creation wizart
// will be exposed
const GUIPort string = "3001"

// Execute performs the actual task and returns true on success
func (t *Create) Execute() (success bool) {
	if t.EnableGUI {

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
			VulnerabilityID: t.VulnID,
			Notes: []model.Note{
				{
					Links: []string{
						"https://..............",
						"https://.......................",
					},
					Text: "Some note about " + t.VulnID,
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
		log.Info().Str("path", filepath.Join(".", "kaybee-new-statements", t.VulnID, "statement.yaml")).Msg("A statement has been created")
		log.Info().Msg("With your favourite text editor, modify it as you see fit, then run the following command")
		log.Info().Msg("	kaybee export --target steady --from ./kaybee-new-statements/")
		log.Info().Msg("That will create the script 'steady.sh' that is ready to be executed to import data into the Steady backend.")
	}

	return true
}
