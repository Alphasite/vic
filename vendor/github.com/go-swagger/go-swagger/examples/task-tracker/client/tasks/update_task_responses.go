package tasks

// This file was generated by the swagger tool.
// Editing this file might prove futile when you re-run the swagger generate command

import (
	"fmt"
	"io"

	"github.com/go-swagger/go-swagger/client"
	"github.com/go-swagger/go-swagger/httpkit"
	"github.com/go-swagger/go-swagger/strfmt"

	"github.com/go-swagger/go-swagger/examples/task-tracker/models"
)

// UpdateTaskReader is a Reader for the UpdateTask structure.
type UpdateTaskReader struct {
	formats strfmt.Registry
}

// ReadResponse reads a server response into the recieved o.
func (o *UpdateTaskReader) ReadResponse(response client.Response, consumer httpkit.Consumer) (interface{}, error) {
	switch response.Code() {

	case 200:
		result := NewUpdateTaskOK()
		if err := result.readResponse(response, consumer, o.formats); err != nil {
			return nil, err
		}
		return result, nil

	case 422:
		result := NewUpdateTaskUnprocessableEntity()
		if err := result.readResponse(response, consumer, o.formats); err != nil {
			return nil, err
		}
		return nil, result

	default:
		result := NewUpdateTaskDefault(response.Code())
		if err := result.readResponse(response, consumer, o.formats); err != nil {
			return nil, err
		}
		return nil, result
	}
}

// NewUpdateTaskOK creates a UpdateTaskOK with default headers values
func NewUpdateTaskOK() *UpdateTaskOK {
	return &UpdateTaskOK{}
}

/*UpdateTaskOK handles this case with default header values.

Task details
*/
type UpdateTaskOK struct {
	Payload *models.Task
}

func (o *UpdateTaskOK) Error() string {
	return fmt.Sprintf("[PUT /tasks/{id}][%d] updateTaskOK  %+v", 200, o.Payload)
}

func (o *UpdateTaskOK) readResponse(response client.Response, consumer httpkit.Consumer, formats strfmt.Registry) error {

	o.Payload = new(models.Task)

	// response payload
	if err := consumer.Consume(response.Body(), o.Payload); err != nil && err != io.EOF {
		return err
	}

	return nil
}

// NewUpdateTaskUnprocessableEntity creates a UpdateTaskUnprocessableEntity with default headers values
func NewUpdateTaskUnprocessableEntity() *UpdateTaskUnprocessableEntity {
	return &UpdateTaskUnprocessableEntity{}
}

/*UpdateTaskUnprocessableEntity handles this case with default header values.

Validation error
*/
type UpdateTaskUnprocessableEntity struct {
	Payload *models.ValidationError
}

func (o *UpdateTaskUnprocessableEntity) Error() string {
	return fmt.Sprintf("[PUT /tasks/{id}][%d] updateTaskUnprocessableEntity  %+v", 422, o.Payload)
}

func (o *UpdateTaskUnprocessableEntity) readResponse(response client.Response, consumer httpkit.Consumer, formats strfmt.Registry) error {

	o.Payload = new(models.ValidationError)

	// response payload
	if err := consumer.Consume(response.Body(), o.Payload); err != nil && err != io.EOF {
		return err
	}

	return nil
}

// NewUpdateTaskDefault creates a UpdateTaskDefault with default headers values
func NewUpdateTaskDefault(code int) *UpdateTaskDefault {
	return &UpdateTaskDefault{
		_statusCode: code,
	}
}

/*UpdateTaskDefault handles this case with default header values.

UpdateTaskDefault update task default
*/
type UpdateTaskDefault struct {
	_statusCode int
}

// Code gets the status code for the update task default response
func (o *UpdateTaskDefault) Code() int {
	return o._statusCode
}

func (o *UpdateTaskDefault) Error() string {
	return fmt.Sprintf("[PUT /tasks/{id}][%d] updateTask default ", o._statusCode)
}

func (o *UpdateTaskDefault) readResponse(response client.Response, consumer httpkit.Consumer, formats strfmt.Registry) error {

	return nil
}
