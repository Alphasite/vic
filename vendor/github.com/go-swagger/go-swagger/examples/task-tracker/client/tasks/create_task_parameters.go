package tasks

// This file was generated by the swagger tool.
// Editing this file might prove futile when you re-run the swagger generate command

import (
	"github.com/go-swagger/go-swagger/client"
	"github.com/go-swagger/go-swagger/errors"
	"github.com/go-swagger/go-swagger/strfmt"

	"github.com/go-swagger/go-swagger/examples/task-tracker/models"
)

// NewCreateTaskParams creates a new CreateTaskParams object
// with the default values initialized.
func NewCreateTaskParams() *CreateTaskParams {
	var ()
	return &CreateTaskParams{}
}

/*CreateTaskParams contains all the parameters to send to the API endpoint
for the create task operation typically these are written to a http.Request
*/
type CreateTaskParams struct {

	/*Body
	  The task to create

	*/
	Body *models.Task
}

// WithBody adds the body to the create task params
func (o *CreateTaskParams) WithBody(body *models.Task) *CreateTaskParams {
	o.Body = body
	return o
}

// WriteToRequest writes these params to a swagger request
func (o *CreateTaskParams) WriteToRequest(r client.Request, reg strfmt.Registry) error {

	var res []error

	if o.Body == nil {
		o.Body = new(models.Task)
	}

	if err := r.SetBodyParam(o.Body); err != nil {
		return err
	}

	if len(res) > 0 {
		return errors.CompositeValidationError(res...)
	}
	return nil
}
